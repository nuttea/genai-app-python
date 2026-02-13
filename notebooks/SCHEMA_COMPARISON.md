# Schema Comparison Analysis

## Current Schema vs. New Schema

### 📊 Key Differences

| Feature | Current Schema | New Schema | Recommendation |
|---------|---------------|------------|----------------|
| **Root Structure** | Direct array `[]` | Wrapped `{documents: []}` | ⚠️ Keep current (simpler) |
| **Form Type Values** | `"Constituency"`, `"PartyList"` | `"ส.ส. ๕/๑๘"`, `"ส.ส. ๕/๑๘ (บช)"` | ⚠️ Keep current (clearer) |
| **Number Format** | Separate fields | `{arabic, thai_text}` | ✅ Add this! |
| **Header Fields** | 7 fields | 9 fields (+ set_number, village_moo) | ✅ Add missing fields |
| **Vote Results** | candidate_name + party_name | name + party | ⚠️ Keep current (clearer) |
| **Total Votes** | ❌ Not included | ✅ total_votes_recorded | ✅ Add this! |
| **Officials** | ❌ Not included | ✅ officials array | ⚠️ Optional (not critical) |
| **Voter Statistics** | ❌ In schema, not required | ✅ In both | ✅ Already there! |

## 🎯 Recommended Updates

### ✅ HIGH PRIORITY - Add These:

#### 1. **Number-Text Pair Structure** (Most Important!)
**Why:** Thai forms have both Arabic numerals AND Thai text - extracting both improves accuracy

**Current:**
```python
"vote_count": 120,
"vote_count_text": "หนึ่งร้อยยี่สิบ"  # Separate fields
```

**Better:**
```python
"vote_count": {
    "arabic": 120,
    "thai_text": "หนึ่งร้อยยี่สิบ"
}
```

**Benefits:**
- ✅ Can validate number against text
- ✅ Better data structure for Thai documents
- ✅ Easier to detect OCR errors

#### 2. **Additional Header Fields**

**Add to `form_info`:**
```python
"set_number": str | None  # ชุดที่ - important for tracking
"village_moo": str | None  # หมู่ที่ - important for rural areas
```

**Example:**
```python
"header_info": {
    "set_number": "1",          # NEW
    "village_moo": "5",         # NEW
    "date": "14 May 2566",
    "province": "กรุงเทพมหานคร",
    ...
}
```

#### 3. **Total Votes Recorded**

**Add to root level:**
```python
"total_votes_recorded": {
    "arabic": 1250,
    "thai_text": "หนึ่งพันสองร้อยห้าสิบ"
}
```

**Benefits:**
- ✅ Validation: sum(vote_results) should equal total_votes_recorded
- ✅ Catches missing entries in vote_results table
- ✅ Found at bottom of vote count table

### ⚠️ OPTIONAL - Consider Adding:

#### 4. **Officials/Committee Members**

```python
"officials": [
    {
        "name": "นายสมชาย ใจดี",
        "position": "ประธานกรรมการ"
    }
]
```

**Pros:**
- Additional metadata
- Could be useful for verification

**Cons:**
- Not essential for vote counting
- Adds complexity
- May have OCR errors in signatures

### ❌ NOT RECOMMENDED:

#### 5. Thai Form Type Values
**Current:** `"Constituency"`, `"PartyList"` ✅
**New:** `"ส.ส. ๕/๑๘"`, `"ส.ส. ๕/๑๘ (บช)"` ❌

**Keep current because:**
- English is clearer for code
- Easier to work with in downstream systems
- Less prone to encoding issues

## 🔧 Updated Pydantic Models

Here's what the updated models should look like:

### Enhanced Models with Number-Text Pairs

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class NumberTextPair(BaseModel):
    """Thai document number representation (both Arabic numeral and Thai text)."""
    arabic: int = Field(..., description="Arabic numeral (e.g., 120)")
    thai_text: Optional[str] = Field(None, description="Thai text (e.g., 'หนึ่งร้อยยี่สิบ')")

    @field_validator('arabic')
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v


class FormInfo(BaseModel):
    """Header information identifying the polling station."""
    form_type: Optional[str] = Field(None, description="Constituency or PartyList")
    set_number: Optional[str] = Field(None, description="Set number (ชุดที่)")  # NEW
    date: Optional[str] = Field(None, description="Date of election")
    province: Optional[str] = Field(None, description="Province name")
    constituency_number: Optional[str] = Field(None, description="Constituency number")
    district: str = Field(..., description="District name")
    sub_district: Optional[str] = Field(None, description="Sub-district name")
    polling_station_number: str = Field(..., description="Polling station number")
    village_moo: Optional[str] = Field(None, description="Village number (หมู่ที่)")  # NEW


class VoterStatistics(BaseModel):
    """Voter statistics (Section 1)."""
    eligible_voters: Optional[NumberTextPair] = Field(None, description="Total eligible voters")
    present_voters: Optional[NumberTextPair] = Field(None, description="Voters who showed up")


class BallotStatistics(BaseModel):
    """Ballot accounting statistics (Section 2)."""
    ballots_allocated: Optional[NumberTextPair] = Field(None, description="Allocated ballots")
    ballots_used: Optional[NumberTextPair] = Field(None, description="Used ballots")
    good_ballots: Optional[NumberTextPair] = Field(None, description="Valid ballots")
    bad_ballots: Optional[NumberTextPair] = Field(None, description="Invalid ballots")
    no_vote_ballots: Optional[NumberTextPair] = Field(None, description="No vote ballots")
    ballots_remaining: Optional[NumberTextPair] = Field(None, description="Remaining ballots")


class VoteResult(BaseModel):
    """Individual vote result."""
    number: int = Field(..., description="Candidate/Party number")
    candidate_name: Optional[str] = Field(None, description="Candidate name (Constituency only)")
    party_name: Optional[str] = Field(None, description="Party name")
    vote_count: NumberTextPair = Field(..., description="Vote count (number + text)")  # UPDATED


class ElectionFormData(BaseModel):
    """Complete election form extraction result."""
    form_info: FormInfo
    voter_statistics: Optional[VoterStatistics] = None  # Now used!
    ballot_statistics: Optional[BallotStatistics] = None
    vote_results: list[VoteResult] = Field(default_factory=list)
    total_votes_recorded: Optional[NumberTextPair] = Field(None, description="Total from table footer")  # NEW

    @field_validator('vote_results')
    @classmethod
    def validate_vote_results_not_empty(cls, v: list[VoteResult]) -> list[VoteResult]:
        if not v:
            raise ValueError("vote_results cannot be empty")
        return v
```

## 🔍 Validation Improvements

With the enhanced schema, you can add better validation:

```python
def validate_extraction_enhanced(data: ElectionFormData) -> tuple[bool, list[str]]:
    """Enhanced validation with number-text pairs."""
    errors = []

    # 1. Ballot statistics validation (using arabic numbers)
    if data.ballot_statistics:
        used = data.ballot_statistics.ballots_used.arabic if data.ballot_statistics.ballots_used else 0
        good = data.ballot_statistics.good_ballots.arabic if data.ballot_statistics.good_ballots else 0
        bad = data.ballot_statistics.bad_ballots.arabic if data.ballot_statistics.bad_ballots else 0
        no_vote = data.ballot_statistics.no_vote_ballots.arabic if data.ballot_statistics.no_vote_ballots else 0

        expected = good + bad + no_vote
        if used != expected:
            errors.append(f"Ballot mismatch: {used} ≠ {expected}")

    # 2. Total votes validation (NEW!)
    if data.total_votes_recorded and data.vote_results:
        total_from_table = sum(v.vote_count.arabic for v in data.vote_results)
        total_recorded = data.total_votes_recorded.arabic

        if total_from_table != total_recorded:
            errors.append(
                f"Vote total mismatch: sum({total_from_table}) ≠ recorded({total_recorded})"
            )

    # 3. Voter statistics validation (NEW!)
    if data.voter_statistics and data.ballot_statistics:
        present = data.voter_statistics.present_voters.arabic if data.voter_statistics.present_voters else 0
        used = data.ballot_statistics.ballots_used.arabic if data.ballot_statistics.ballots_used else 0

        # Present voters should match or be close to ballots used
        if abs(present - used) > 5:  # Allow small discrepancy
            errors.append(f"Voter count ({present}) doesn't match ballots used ({used})")

    return len(errors) == 0, errors
```

## 📋 Summary of Recommendations

### ✅ Definitely Add:

1. **NumberTextPair** - For better accuracy and validation
   - Applies to: ballot statistics, voter statistics, vote counts, total votes

2. **Additional header fields:**
   - `set_number` (ชุดที่)
   - `village_moo` (หมู่ที่)

3. **total_votes_recorded** - For validation

4. **voter_statistics** - Already in schema but make it more useful with NumberTextPair

### ⚠️ Consider:

5. **officials** - Only if you need committee member tracking

### ❌ Don't Change:

6. **form_type values** - Keep English ("Constituency", "PartyList")
7. **Root structure** - Keep direct array (simpler)
8. **Vote results structure** - Keep candidate_name + party_name (clearer than single "name")

## 🎯 Migration Path

### Phase 1: Add NumberTextPair (Backward Compatible)
```python
# Support both old and new formats
class VoteResult(BaseModel):
    vote_count: int | NumberTextPair  # Accept either format
    vote_count_text: Optional[str] = None  # Deprecated, use vote_count.thai_text
```

### Phase 2: Full Migration
```python
# Require NumberTextPair
class VoteResult(BaseModel):
    vote_count: NumberTextPair  # Only accept new format
```

## 📊 Impact Analysis

| Change | Backend Impact | Frontend Impact | Data Quality |
|--------|---------------|-----------------|--------------|
| NumberTextPair | Medium (schema change) | Low (just display) | High ✅ |
| set_number, village_moo | Low (optional fields) | Low (optional display) | Medium ✅ |
| total_votes_recorded | Low (optional) | Low (optional) | High ✅ |
| officials | Medium (new extraction) | Low (optional) | Low ⚠️ |

## 🚀 Recommended Action Plan

1. **Start with NumberTextPair** - Biggest quality improvement
2. **Add header fields** - Easy wins (set_number, village_moo)
3. **Add total_votes_recorded** - Important for validation
4. **Test thoroughly** - Ensure backward compatibility
5. **Update validation logic** - Use enhanced validation
6. **Consider officials** - Only if needed for your use case

Would you like me to create the updated Pydantic models and Gemini schema with these improvements?
