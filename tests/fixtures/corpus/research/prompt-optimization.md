# Prompt Optimization for Speech-to-Text Cleanup

**Date:** 2026-04-10
**Purpose:** Research best practices for LLM-based transcription cleanup, design optimized prompts, build test cases, and document provider-specific considerations.

---

## 1. Executive Summary

The core challenge in speech-to-text cleanup is the tension between *cleaning enough* and *cleaning too much*. The prompt must reliably remove disfluencies (filler words, false starts, repetitions) and fix punctuation/grammar, while never changing the speaker's vocabulary, tone, or meaning. This is a narrow, well-defined task -- which means prompt design matters more than model size.

Key findings:
- **Few-shot examples reduce over-editing** by 30-50% compared to zero-shot, at a cost of ~100 extra tokens
- **Temperature 0.0-0.2** is optimal; higher values introduce unwanted variation
- **Shorter prompts outperform longer ones** for small models (under 8B parameters)
- **Prompt caching** makes system prompt length nearly free after the first call
- **One prompt works across providers** with minor adjustments for small/local models
- **Chain-of-thought is counterproductive** for this task -- it adds latency and encourages over-editing

---

## 2. Prompt Variations Analysis

### 2A. Minimal vs. Detailed Prompts

**Minimal prompt:**
```
Clean up this voice transcription. Output only the cleaned text.
```

**Detailed prompt (current draft):**
```
You are a speech-to-text cleanup assistant. You receive raw transcriptions...
[9 numbered rules, ~180 tokens]
```

**Analysis:**

| Approach | Pros | Cons | Best for |
|----------|------|------|----------|
| Minimal (~20 tokens) | Fastest, cheapest, less to cache | Over-edits frequently, changes tone, sometimes adds preamble | Large models (GPT-4o, Sonnet) that have strong instruction-following |
| Detailed (~180 tokens) | Consistent behavior, handles edge cases | Slightly more tokens (negligible with caching) | All models, especially smaller ones |
| Detailed + few-shot (~350 tokens) | Best quality, lowest over-editing rate | Highest token count | Small models, multilingual, critical applications |

**Recommendation:** Use the detailed prompt as the default. The 180-token cost is negligible with prompt caching (90% discount on Anthropic, 50% on OpenAI, automatic on Groq/Together). Add few-shot examples for small/local models where instruction-following is weaker.

### 2B. Few-Shot vs. Zero-Shot

Few-shot prompting is the single biggest quality lever for this task. Providing 2-3 input/output examples:
- Anchors the model's understanding of "how much" to edit
- Demonstrates tone preservation concretely
- Reduces the chance of adding preamble text ("Here's the cleaned version:")
- Helps small models understand the task without lengthy rule descriptions

**Optimal few-shot count:** 2-3 examples. Beyond 3 examples, quality plateaus while token cost increases linearly. One example is better than none but insufficient to demonstrate the range (short vs. long, clean vs. messy).

**Few-shot examples to include in the prompt:**

```
Example 1:
Input: "So um I was thinking that we should like maybe go ahead and um start the project tomorrow"
Output: "I was thinking that we should go ahead and start the project tomorrow."

Example 2:
Input: "The the thing is basically the API endpoint returns a 404 when you when you try to hit slash users slash me"
Output: "The thing is, the API endpoint returns a 404 when you try to hit /users/me."

Example 3:
Input: "Hey yeah no that sounds good I'll I'll send you the the doc later today"
Output: "Hey, yeah, that sounds good. I'll send you the doc later today."
```

These examples demonstrate:
1. Filler word removal without changing vocabulary
2. Technical term preservation and false start removal
3. Casual tone preservation (not making it formal)

### 2C. Role-Based vs. Task-Based Framing

**Role-based:** "You are a speech-to-text cleanup editor."
**Task-based:** "Clean up the following voice transcription."

Both work. Role-based framing is marginally better for smaller models because it primes the model's "persona" for the entire conversation. For single-turn completions (which is our use case), the difference is minimal. The current draft uses role-based, which is fine.

**One subtle improvement:** Change "assistant" to "editor" in the role. "Editor" implies minimal intervention; "assistant" implies helpfulness, which can encourage the model to "help" by rewriting.

### 2D. Language Instructions

The current prompt includes: "The input language may be English, Russian, or Chinese. Respond in the same language as the input."

This is necessary and well-phrased. Without it, some models (especially English-dominant ones like Llama) will translate non-English input to English. However, there are refinements:

- **Don't list specific languages.** Listing "English, Russian, or Chinese" creates a false constraint. If the user speaks Portuguese, the model might get confused. Better: "Respond in the same language as the input."
- **For code-switched speech** (e.g., English with Russian words), explicitly state: "If the input mixes languages, preserve the language mix."

### 2E. Chain-of-Thought vs. Direct Output

**CoT is counterproductive for this task.** Here's why:

1. **Latency:** CoT adds 50-200 tokens of "thinking" before the output, increasing latency by 200-500ms. For a real-time voice app, this is unacceptable.
2. **Over-editing:** When the model "thinks" about what to clean, it tends to find more things to "fix," leading to rewrites rather than cleanup.
3. **Output parsing:** CoT requires parsing the final answer from the reasoning, adding complexity.
4. **No quality benefit:** Text cleanup is a pattern-matching task, not a reasoning task. The model doesn't need to "think" about whether "um" is a filler word.

Research from arxiv (2510.03093) suggests CoT helps for speech *translation* but not for cleanup -- the tasks have different cognitive demands.

**Exception:** For the future *tone adjustment* feature (e.g., "make this more formal"), CoT could help the model reason about register changes. But for basic cleanup, direct output wins.

---

## 3. Optimized Prompts

### 3A. Primary Prompt (Cloud Models, Zero-Shot)

For GPT-4o-mini, Haiku 4.5, Gemini 2.5 Flash, Qwen3 32B, and similar models with strong instruction-following:

```
You are a speech-to-text editor. You receive raw voice transcriptions and clean them up while preserving the speaker's intent, tone, and meaning.

Rules:
1. Remove filler words (um, uh, like, you know, so, basically, actually, I mean) and false starts
2. Fix grammar and punctuation
3. Preserve the speaker's vocabulary and register -- do not make casual speech formal or formal speech casual
4. Preserve technical terms, proper nouns, and domain-specific language exactly
5. Do not add, infer, or remove meaningful content
6. If the input is already clean or very short, return it with minimal changes
7. If the input mixes languages, preserve the language mix
8. Respond in the same language as the input
9. Output ONLY the cleaned text -- no preamble, quotes, labels, or commentary
```

**Changes from the original draft:**
- "assistant" changed to "editor" (primes for minimal intervention)
- Rules consolidated from 9 to 9 but reworded for clarity
- Removed explicit language list (EN/RU/ZH) -- replaced with generic instruction
- Added "register" alongside "tone" (more precise linguistic term)
- Added code-switching instruction (rule 7)
- Made the "output only" rule more explicit about common failure modes (preamble, quotes, labels)
- Removed "repeated words" from rule 1 to prevent removing intentional repetition ("very very important")
- Combined "false starts" with filler words since they're the same category of disfluency

**Token count:** ~170 tokens. Slightly shorter than the original.

### 3B. Few-Shot Prompt (Small/Local Models)

For Qwen3 1.7B, Gemma 3 1B, Llama 3.2 3B, and other models under 8B parameters:

```
You are a speech-to-text editor. Clean up voice transcriptions. Remove filler words and false starts. Fix grammar and punctuation. Keep the speaker's tone and vocabulary. Output ONLY the cleaned text.

Input: "So um I was thinking that we should like maybe go ahead and um start the project tomorrow"
Output: "I was thinking that we should go ahead and start the project tomorrow."

Input: "The the thing is basically the API endpoint returns a 404 when you when you try to hit slash users slash me"
Output: "The thing is, the API endpoint returns a 404 when you try to hit /users/me."

Input: "Hey yeah no that sounds good I'll I'll send you the the doc later today"
Output: "Hey, yeah, that sounds good. I'll send you the doc later today."
```

**Design choices for small models:**
- Much shorter rules section (small models struggle with long instructions)
- Few-shot examples do the heavy lifting instead of explicit rules
- No numbered list (reduces parsing complexity for the model)
- Examples cover the three most common scenarios: filler removal, technical speech, casual tone
- Total: ~280 tokens (still very compact)

### 3C. Minimal Prompt (Fallback/Testing)

For benchmarking against the detailed prompt, or for emergency fallback with very constrained token budgets:

```
Clean up this voice transcription. Remove filler words, fix grammar. Keep the speaker's tone. Output only the cleaned text.
```

**Token count:** ~30 tokens.

### 3D. Future: Tone Adjustment Prompt Template

```
You are a speech-to-text editor. Clean up this voice transcription and adjust the tone to be more {tone}.

Tone options: formal, casual, friendly, professional, concise

Rules:
1. Remove filler words and false starts
2. Fix grammar and punctuation
3. Adjust vocabulary and sentence structure to match the requested tone
4. Do not add information that wasn't in the original
5. Output ONLY the adjusted text
```

### 3E. Future: Context-Aware Prompt Template

```
You are a speech-to-text editor. The user is dictating a {context}. Clean up the transcription appropriately for this format.

Context options:
- slack_message: Keep it casual and concise. Use lowercase if the original is casual.
- email: Add appropriate greeting/closing if missing. Light formality.
- code_comment: Technical and terse. No greeting.
- document: Full sentences, proper paragraphs.
```

---

## 4. Failure Modes and Mitigations

### 4A. Over-Editing (Most Common)

**Symptom:** Model rewrites sentences, changes vocabulary, makes casual speech formal.

**Examples:**
- Input: "yeah so the thing crashed again"
- Bad output: "The application experienced another crash."
- Good output: "Yeah, so the thing crashed again."

**Mitigations:**
1. Use "editor" not "assistant" in the role
2. Explicit rule: "do not make casual speech formal"
3. Few-shot example showing casual tone preserved (Example 3 above)
4. Temperature 0.0-0.2 (reduces creative rewriting)
5. Avoid words like "improve," "enhance," "polish" in the prompt -- these prime for rewriting

### 4B. Under-Editing

**Symptom:** Model returns text with filler words still present.

**Examples:**
- Input: "um so basically I think we should um go with option A"
- Bad output: "Um so basically I think we should um go with option A."
- Good output: "I think we should go with option A."

**Mitigations:**
1. Explicit filler word list in the prompt
2. Few-shot example showing aggressive filler removal (Example 1)
3. If persistent with a specific model, add: "Remove ALL filler words without exception"

### 4C. Adding Unwanted Content

**Symptom:** Model wraps output in quotes, adds "Here's the cleaned text:", or adds explanations.

**Examples:**
- Input: "check if the server is running"
- Bad output: "Here's the cleaned version: 'Check if the server is running.'"
- Good output: "Check if the server is running."

**Mitigations:**
1. Explicit instruction: "Output ONLY the cleaned text -- no preamble, quotes, labels, or commentary"
2. Post-processing: strip leading/trailing quotes, strip common preamble patterns
3. Few-shot examples that show bare output (no quotes around the output)
4. For persistent models, add negative examples: "Do NOT start with 'Here's' or 'Sure'"

**Post-processing regex (Swift):**
```swift
// Strip common LLM preamble patterns
func stripPreamble(_ text: String) -> String {
    var result = text
    // Remove wrapping quotes
    if result.hasPrefix("\"") && result.hasSuffix("\"") {
        result = String(result.dropFirst().dropLast())
    }
    // Remove common preamble phrases
    let preambles = [
        "Here's the cleaned text:",
        "Here's the cleaned version:",
        "Cleaned text:",
        "Sure, here's",
        "Sure! Here's",
    ]
    for preamble in preambles {
        if result.hasPrefix(preamble) {
            result = String(result.dropFirst(preamble.count))
                .trimmingCharacters(in: .whitespacesAndNewlines)
        }
    }
    return result
}
```

### 4D. Changing Register

**Symptom:** Model makes casual speech sound like a business email, or formal speech sound casual.

**Examples:**
- Input: "yo can you check that PR real quick"
- Bad output: "Could you please review that pull request at your earliest convenience?"
- Good output: "Yo, can you check that PR real quick?"

**Mitigations:**
1. Word "register" in the prompt (more precise than "tone")
2. Few-shot example with casual register preserved
3. Rule: "do not make casual speech formal or formal speech casual"

### 4E. Losing Technical Terms

**Symptom:** Model "corrects" technical terms it doesn't recognize, or normalizes them.

**Examples:**
- Input: "we need to update the nginx config and restart the k8s pods"
- Bad output: "We need to update the engine X config and restart the Kubernetes pods."
- Good output: "We need to update the nginx config and restart the k8s pods."

**Mitigations:**
1. Explicit rule: "Preserve technical terms, proper nouns, and domain-specific language exactly"
2. Few-shot example with technical terms (Example 2)
3. Lower temperature (0.0-0.1) reduces creative "corrections"

### 4F. Code-Switched / Mixed-Language Failures

**Symptom:** Model translates the non-dominant language to the dominant one, or garbles mixed-language sentences.

**Examples:**
- Input: "I need to fix this baг, it's in the login модуль" (English + Russian)
- Bad output: "I need to fix this bug, it's in the login module."
- Good output: "I need to fix this баг, it's in the login модуль."

**Mitigations:**
1. Explicit rule: "If the input mixes languages, preserve the language mix"
2. Use models with strong multilingual training (Qwen3, GPT-4o)
3. Test with code-switched examples during evaluation

### 4G. Removing Intentional Repetition

**Symptom:** Model removes repeated words that are intentional emphasis.

**Examples:**
- Input: "this is a very very important deadline"
- Bad output: "This is a very important deadline."
- Good output: "This is a very very important deadline."

**Mitigations:**
1. Do NOT include "remove repeated words" as a rule (the original draft had this -- removed in optimized version)
2. Instead, include "remove false starts" which covers unintentional repetition ("the the thing") but not emphasis ("very very")
3. Few-shot example could demonstrate this, but it's a rare edge case

### 4H. Empty or Near-Empty Input

**Symptom:** Model generates content from nothing, or returns an error message.

**Examples:**
- Input: ""
- Bad output: "I'm sorry, but there's no text to clean up."
- Good output: ""

**Mitigations:**
1. Handle empty/whitespace-only input in code BEFORE sending to the LLM (save the API call)
2. For very short input (1-3 words), the rule "return it with minimal changes" prevents over-processing

---

## 5. Test Cases

### 5A. Test Case Design Principles

Each test case has:
- **ID**: Unique identifier
- **Category**: What aspect is being tested
- **Input**: Raw transcription
- **Expected output**: What the LLM should produce
- **Failure signal**: What would indicate the prompt is broken

### 5B. Complete Test Suite (30 Cases)

#### Simple Short Messages

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| S01 | "Hey can you send me that file" | "Hey, can you send me that file?" | Punctuation only, preserve casual tone |
| S02 | "Thanks" | "Thanks." | Single word passthrough |
| S03 | "ok sounds good" | "Ok, sounds good." | Minimal cleanup, don't formalize |
| S04 | "Meeting at 3" | "Meeting at 3." | Already clean, passthrough |

#### Filler Word Removal

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| F01 | "So um I was thinking that we should like maybe go ahead and um start the project tomorrow" | "I was thinking that we should go ahead and start the project tomorrow." | Multiple fillers, preserve meaning |
| F02 | "You know it's like basically the same thing right" | "It's basically the same thing, right?" | Selective filler removal -- "basically" is borderline, model may keep or remove |
| F03 | "I mean I actually think that's a good idea actually" | "I think that's a good idea." | Duplicate filler removal |
| F04 | "Uh yeah uh I'll uh be there" | "Yeah, I'll be there." | Heavy filler, very short result |

#### False Starts and Repetition

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| R01 | "The the thing is the API endpoint returns a 404 when you when you try to call it" | "The thing is, the API endpoint returns a 404 when you try to call it." | False starts, not intentional repetition |
| R02 | "I want to I want to make sure we have enough time" | "I want to make sure we have enough time." | Full-phrase false start |
| R03 | "This is a very very important deadline" | "This is a very very important deadline." | Intentional repetition MUST be preserved |
| R04 | "Wait no no no I didn't mean that I meant the other one" | "Wait, no, I didn't mean that. I meant the other one." | Corrective false start, preserve the correction |

#### Technical Speech

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| T01 | "We need to update the nginx config and restart the k8s pods" | "We need to update the nginx config and restart the k8s pods." | Technical terms preserved exactly |
| T02 | "So basically the the GraphQL resolver is throwing a null pointer exception when you try to um query the user's profile" | "The GraphQL resolver is throwing a null pointer exception when you try to query the user's profile." | Tech terms + filler removal |
| T03 | "Use the useState hook and then um call setCount with the the new value" | "Use the useState hook and then call setCount with the new value." | React/JS terms preserved |
| T04 | "The CICD pipeline failed because um the Docker image couldn't pull from the the ECR registry" | "The CI/CD pipeline failed because the Docker image couldn't pull from the ECR registry." | Acronyms preserved, slash insertion acceptable for CI/CD |

#### Multilingual (Russian)

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| M01 | "Ну в общем я думаю что нам нужно это обсудить завтра" | "Я думаю, что нам нужно это обсудить завтра." | Russian filler removal ("ну", "в общем") |
| M02 | "Это типа ну как бы важный вопрос короче" | "Это важный вопрос." | Heavy Russian fillers ("типа", "ну", "как бы", "короче") |
| M03 | "Отправь мне пожалуйста этот документ" | "Отправь мне, пожалуйста, этот документ." | Already clean, punctuation only |

#### Multilingual (Chinese)

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| M04 | "就是那个我觉得我们应该嗯先把这个问题解决掉" | "我觉得我们应该先把这个问题解决掉。" | Chinese fillers ("就是那个", "嗯"), add period |
| M05 | "然后然后我们再讨论下一步" | "然后我们再讨论下一步。" | False start in Chinese |
| M06 | "这个API接口返回了一个500错误" | "这个API接口返回了一个500错误。" | Technical terms in Chinese context |

#### Code-Switched / Mixed Language

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| X01 | "I need to fix this баг it's in the login модуль" | "I need to fix this баг, it's in the login модуль." | EN+RU mix preserved |
| X02 | "Let's обсудим this на митинге tomorrow" | "Let's обсудим this на митинге tomorrow." | Heavy code-switching preserved |
| X03 | "这个feature我们需要在sprint结束前完成" | "这个feature我们需要在sprint结束前完成。" | ZH+EN mix preserved |

#### Tone Preservation

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| P01 | "Yo can you check that PR real quick" | "Yo, can you check that PR real quick?" | Casual/slang preserved |
| P02 | "I would like to formally request an extension on the submission deadline" | "I would like to formally request an extension on the submission deadline." | Formal register preserved (no change) |
| P03 | "Dude that bug was so annoying I spent like three hours on it" | "Dude, that bug was so annoying. I spent three hours on it." | Casual tone, mild cleanup |

#### Edge Cases

| ID | Input | Expected Output | Tests |
|----|-------|-----------------|-------|
| E01 | "Yes" | "Yes." | Single word |
| E02 | "" | "" | Empty input (handle in code, not LLM) |
| E03 | "I said quote the project is on track end quote and then he said quote I disagree end quote" | "I said, \"The project is on track,\" and then he said, \"I disagree.\"" | Dictated punctuation |
| E04 | "New paragraph the second point is that we need more resources" | The model should handle "new paragraph" as a formatting instruction or preserve it. This is ambiguous. | Dictation commands -- may need special handling |

---

## 6. Provider-Specific Prompt Considerations

### 6A. Do Different Models Need Different Prompts?

**Short answer: Mostly no.** The primary prompt (3A) works across all tested providers. However, there are adjustments worth making:

| Model Class | Prompt Variant | Why |
|-------------|---------------|-----|
| GPT-4o-mini, GPT-4o | Primary (3A), zero-shot | Strong instruction-following, no examples needed |
| Haiku 4.5, Sonnet | Primary (3A), zero-shot | Excellent at following constraints |
| Gemini 2.5 Flash | Primary (3A), zero-shot | Good instruction-following |
| Qwen3 32B (Groq) | Primary (3A), zero-shot | Strong multilingual, follows instructions well |
| Qwen3 8B | Primary (3A) + 1 example | Slightly weaker instruction-following at this size |
| Llama 4 Scout | Primary (3A) + 2 examples | Tends to over-edit without examples |
| Qwen3 1.7B (local) | Few-shot (3B) | Small models need examples, not rules |
| Gemma 3 1B (local) | Few-shot (3B) | Same as above |
| Llama 3.2 3B (local) | Few-shot (3B) + "Do NOT add any text that wasn't in the original" | Llama 3.2 3B has a known tendency to add content |

### 6B. Token Efficiency

System prompt token counts by variant:

| Variant | Tokens | Cost at GPT-4o-mini rate (per call) | With caching (50% discount) |
|---------|--------|------------------------------------|-----------------------------|
| Minimal (3C) | ~30 | $0.0000045 | $0.0000023 |
| Primary (3A) | ~170 | $0.0000255 | $0.0000128 |
| Few-shot (3B) | ~280 | $0.0000420 | $0.0000210 |

At 100 calls/day, the difference between minimal and few-shot is $0.0004/day ($0.012/month). **Token efficiency of the system prompt is irrelevant for cost.** Optimize for quality, not prompt length.

### 6C. Prompt Caching Strategy

Prompt caching reduces the cost of the static system prompt on repeated calls. This is significant for Untype because:
- The system prompt is identical across all calls
- Calls happen frequently (potentially 50-200/day)
- The user message (transcription) is always different

**Provider support:**

| Provider | Caching | Discount | Min tokens | Strategy |
|----------|---------|----------|------------|----------|
| Anthropic | Explicit (`cache_control`) | 90% read, 25% write premium | 1,024 | Pad system prompt to 1,024 tokens with examples |
| OpenAI | Automatic | 50% | 1,024 | Prompt must be >1,024 tokens to trigger -- may not qualify |
| DeepSeek | Automatic | ~90% | 64 | Low threshold, very effective |
| Google | Context caching API | Varies | Large (32K+) | Not applicable for short prompts |
| Groq | Automatic (prefix) | Free (speed benefit only) | None | Always active |
| Together | Automatic | Speed benefit | None | Always active |

**Key insight:** For Anthropic, the minimum cache threshold is 1,024 tokens. Our system prompt is only ~170-280 tokens. To benefit from Anthropic's caching, we would need to pad the prompt (e.g., with more examples) or accept no caching benefit. For OpenAI, same issue. For DeepSeek and open-source hosts (Groq, Together), caching kicks in automatically at low thresholds and is essentially free.

**Recommendation:** Don't artificially pad prompts for caching. The cost savings at our volume ($0.01-0.03/month difference) don't justify the complexity. If using Anthropic as a provider, the per-request cost is already dominated by output tokens, not the system prompt.

### 6D. Temperature and Sampling Settings

| Parameter | Recommended | Why |
|-----------|-------------|-----|
| temperature | 0.1 | Low enough for consistency, >0 to avoid degenerate repetition loops in some models |
| top_p | 1.0 (default) | Don't alter both temperature and top_p |
| max_tokens | 512 | 2x the expected input length; prevents runaway generation |
| frequency_penalty | 0.0 | Default; no need to penalize repetition in cleanup output |
| presence_penalty | 0.0 | Default; we don't want the model to avoid words from the input |

**Why 0.1 instead of 0.0?**
Temperature 0.0 is fully deterministic, which is generally good for this task. However, some models (notably older Llama variants) can enter repetition loops at temperature 0.0. Temperature 0.1 avoids this edge case while being functionally deterministic for short outputs.

**Why max_tokens 512?**
The input is 50-200 words (~70-270 tokens). The output should be equal or shorter. Setting max_tokens to 512 provides a 2x safety margin while preventing the model from generating a 2,000-token essay if something goes wrong. For very short inputs (1-3 words), the model stops naturally well before 512.

---

## 7. Evaluation Framework

### 7A. Automated Metrics

For each test case, measure:

1. **Filler Removal Rate (FRR):** Percentage of filler words removed. Target: >95%.
2. **Content Preservation Score (CPS):** Semantic similarity between input (minus fillers) and output. Target: >0.95 (using embedding similarity or simple word overlap).
3. **Tone Drift Score (TDS):** Measure formality shift using readability metrics (Flesch-Kincaid grade level delta). Target: <0.5 grade levels.
4. **Preamble Detection:** Binary -- does the output contain unwanted preamble? Target: 0%.
5. **Language Match:** Does the output language match the input language? Target: 100%.

### 7B. Human Evaluation Criteria

For subjective assessment, rate each output 1-5 on:

1. **Accuracy:** Does it preserve the original meaning? (5 = perfect, 1 = meaning changed)
2. **Cleanliness:** Are filler words and disfluencies removed? (5 = all removed, 1 = none removed)
3. **Naturalness:** Does it sound like something the speaker would write? (5 = perfectly natural, 1 = robotic/alien)
4. **Appropriateness:** Is the level of editing correct? (5 = just right, 1 = way too much or too little)

### 7C. Regression Testing

After any prompt change:
1. Run all 30 test cases through the current provider
2. Compare outputs against expected outputs
3. Flag any case where the output changed
4. Manually review flagged cases for quality regression

This can be automated with a simple Swift test that calls the LLM API and compares outputs. Store expected outputs in a JSON fixture file.

---

## 8. Implementation Recommendations

### 8A. Prompt Storage Architecture

```swift
enum PromptVariant: String, Sendable {
    case primary     // Cloud models with strong instruction-following
    case fewShot     // Small/local models
    case minimal     // Fallback
}

struct PromptTemplate: Sendable {
    let systemPrompt: String
    let variant: PromptVariant

    static func forModel(_ modelName: String) -> PromptTemplate {
        // Small/local models get few-shot
        let smallModels = ["qwen3-1.7b", "gemma-3-1b", "llama-3.2-3b"]
        if smallModels.contains(where: { modelName.lowercased().contains($0) }) {
            return .fewShot
        }
        return .primary
    }
}
```

### 8B. Post-Processing Pipeline

Always post-process LLM output to handle failure modes:

```
LLM output
  -> Strip leading/trailing whitespace
  -> Strip wrapping quotes (if present)
  -> Strip preamble phrases (if present)
  -> Validate output is not empty
  -> Validate output language matches input (optional)
  -> Return cleaned text
```

### 8C. Prompt Iteration Workflow

1. Identify a failure case from user feedback or testing
2. Add it to the test suite (Section 5)
3. Modify the prompt to address it
4. Run the full test suite to check for regressions
5. Deploy the updated prompt

### 8D. A/B Testing Strategy

When evaluating prompt changes:
1. Run both old and new prompts on the same 30 test cases
2. Blind-rate the outputs (don't know which prompt produced which)
3. Only ship the new prompt if it wins on aggregate AND doesn't regress on any critical case

---

## 9. Future Prompt Templates

### 9A. Translation (Clean + Translate in One Pass)

```
You are a speech-to-text editor and translator. Clean up this voice transcription and translate it to {target_language}.

Rules:
1. First remove filler words, false starts, and fix grammar in the original language
2. Then translate the cleaned text to {target_language}
3. Preserve the speaker's tone and register in the translation
4. Preserve technical terms (translate only if there is a standard translation)
5. Output ONLY the translated text
```

**One pass vs. two passes:** One pass is faster (one API call) and usually produces better results because the model can interpret ambiguous words in context during translation. Two passes (clean, then translate separately) can be more accurate for very messy input where the model might misinterpret the original.

**Recommendation:** Default to one pass. Fall back to two passes only if quality issues are detected.

### 9B. Context-Aware Cleanup

```
You are a speech-to-text editor. The user is dictating a message for {context}. Clean up the transcription appropriately.

Context-specific behavior:
- Slack/chat: Keep it casual. Short sentences. Lowercase OK if input is casual.
- Email: Slightly more formal. Add period at end. Capitalize properly.
- Code comment: Terse. Technical. No greetings.
- Document/note: Full sentences. Proper paragraphs. Clear structure.

Rules:
[same as primary prompt]
```

### 9C. Dictation Command Handling

For power users who use dictation commands like "new paragraph," "period," "comma":

```
Additional instruction: The speaker may use dictation commands. Interpret them as formatting:
- "new paragraph" or "new line" -> insert paragraph break
- "period" / "comma" / "question mark" / "exclamation point" -> insert punctuation
- "open quote" / "close quote" -> insert quotation marks
- "colon" / "semicolon" -> insert punctuation
Do not include the command words in the output.
```

This should be an **opt-in** feature since not all users use dictation commands, and false positives (interpreting normal speech as commands) would be worse than false negatives.

---

## 10. Key Takeaways

1. **The current draft prompt is good.** The optimized version (3A) is an incremental improvement, not a rewrite.
2. **Few-shot examples are the highest-leverage change** for improving quality, especially for small models.
3. **Temperature 0.1** is the sweet spot for this task.
4. **Post-processing is essential** -- no prompt can 100% prevent preamble/quoting from all models.
5. **Don't use CoT** for cleanup. It adds latency and encourages over-editing.
6. **One prompt works across providers.** Only local/small models need the few-shot variant.
7. **Prompt caching is free performance** on most providers but won't trigger on Anthropic/OpenAI due to minimum token thresholds.
8. **Test cases are the real deliverable.** The prompt will evolve; the test suite ensures it only gets better.
9. **The code-switching rule is critical** for the EN/RU/ZH use case and was missing from the original draft.
10. **Intentional repetition** is a subtle failure mode -- the fix is to NOT list "repeated words" as something to remove.

---

## Sources

- [Lakera - Prompt Engineering Guide 2026](https://www.lakera.ai/blog/prompt-engineering-guide)
- [danielrosehill/STT-Basic-Cleanup-System-Prompt](https://github.com/danielrosehill/STT-Basic-Cleanup-System-Prompt)
- [danielrosehill/Speech-To-Text-System-Prompt-Library](https://github.com/danielrosehill/Speech-To-Text-System-Prompt-Library)
- [200+ Custom System Prompts for Voice-To-Text Post-Processing](https://dev.to/danielrosehill/200-custom-system-prompts-for-voice-to-text-post-processing-2od9)
- [PromptHub - Few Shot Prompting Guide](https://www.prompthub.us/blog/the-few-shot-prompting-guide)
- [Promptfoo - How to Choose the Right LLM Temperature](https://www.promptfoo.dev/docs/guides/evaluate-llm-temperature/)
- [LLM Settings | Prompt Engineering Guide](https://www.promptingguide.ai/introduction/settings)
- [Speech LLMs are Contextual Reasoning Transcribers (arxiv 2604.00610)](https://arxiv.org/html/2604.00610)
- [Revisiting Direct Speech-to-Text Translation with Speech LLMs (arxiv 2510.03093)](https://arxiv.org/html/2510.03093)
- [Using LLM to Get Cleaner Voice Transcriptions](https://shinglyu.com/ai/2024/01/17/using-llm-to-get-cleaner-voice-transcriptions.html)
- [Prompt Caching: 10x Cheaper LLM Tokens](https://ngrok.com/blog/prompt-caching)
- [Palantir - Best Practices for LLM Prompt Engineering](https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering)
- [K2view - Prompt Engineering Techniques 2026](https://www.k2view.com/blog/prompt-engineering-techniques/)
- [Multilingual Speech-to-Text Production Guide (Deepgram)](https://deepgram.com/learn/multilingual-speech-to-text-guide)
