import { API_CONFIG } from '@/lib/constants/config';

export const runtime = 'nodejs';

export async function POST(req: Request) {
  try {
    const { messages, sessionId } = await req.json();

    // Get the last user message
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || lastMessage.role !== 'user') {
      return new Response('Invalid message format', { status: 400 });
    }

    const appName = 'content_creator_agent';
    const userId = 'user_nextjs';
    const currentSessionId = sessionId || `session_${Date.now()}`;

    // Create session if needed
    try {
      const sessionResponse = await fetch(
        `${API_CONFIG.contentCreator.baseUrl}/apps/${appName}/users/${userId}/sessions`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sessionId: currentSessionId }),
        }
      );

      if (!sessionResponse.ok && sessionResponse.status !== 409) {
        throw new Error(`Failed to create session: ${sessionResponse.status}`);
      }
    } catch (error) {
      // Session might already exist, continue
      console.warn('Session creation warning:', error);
    }

    // Call ADK /run_sse endpoint
    const response = await fetch(`${API_CONFIG.contentCreator.baseUrl}/run_sse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        appName,
        userId,
        sessionId: currentSessionId,
        newMessage: {
          role: 'user',
          parts: [{ text: lastMessage.content }],
        },
        streaming: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`ADK API error: ${response.status}`);
    }

    // Transform ADK SSE stream to Vercel AI SDK format
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const jsonString = line.slice(6).trim();
                if (jsonString) {
                  try {
                    const data = JSON.parse(jsonString);

                    // Extract text from ADK response
                    if (data.content?.parts) {
                      for (const part of data.content.parts) {
                        if (part.text) {
                          // Send text chunk to Vercel AI SDK
                          const encoder = new TextEncoder();
                          controller.enqueue(encoder.encode(part.text));
                        }
                      }
                    }
                  } catch (e) {
                    console.error('Error parsing SSE chunk:', e);
                  }
                }
              }
            }
          }
        } catch (error) {
          console.error('Stream error:', error);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
      },
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return new Response(
      JSON.stringify({
        error: 'Failed to process chat request',
        details: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

