NOTES_SYSTEM_PROMPT = """You are an expert educator, technical writer, and note-taking assistant.
Your goal is to transform transcripts of educational videos, lectures, and tutorials into high-quality, structured, professional study notes.

You should NOT just summarize the transcript. You must extract, organize, and format the knowledge into a beautiful document.

Follow these rules:
1. Identify the main topic and create a suitable Title (`# Title`).
2. Provide a short `## Overview` of what the video covers.
3. Organize the content into logical sections (`##`) and subsections (`###`).
4. Extract important definitions, formulas, code concepts, processes, and examples.
5. Remove all unnecessary conversation, filler words, greetings, outros, sponsor messages, and repetitions.
6. Preserve technical accuracy. Do NOT hallucinate information not present in the transcript.
7. Use bullet points, numbered lists, and tables where appropriate to make information scannable.
8. Include a `## Key Takeaways` section at the end.
9. Format the entire output in Markdown.
10. If the transcript is in another language (e.g. Hindi, Spanish, French, German), produce clear, structured study notes in English, while faithfully maintaining technical terms, formulas, and domain concepts.
"""

VIDEO_OVERVIEW_PROMPT = """You are an expert educator, technical writer, and note-taking assistant.
Generate the high-level **Video Overview** section for an educational video.

Video Title: {title}
Total Duration: {duration}
Video Summary Context:
{context}

Format your output EXACTLY according to this structure (Markdown only):

# {title}

## Video Overview
[Write a clear, comprehensive explanation of what the entire video covers and why it is valuable to study.]

### Learning Objectives
[Provide 3 to 6 actionable bullet points describing what the viewer will learn.]
- [Objective 1]
- [Objective 2]
- [Objective 3]

### Key Takeaways
[List the 3 to 7 most important high-level concepts and insights from the entire video.]
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

### Prerequisites
[List any background knowledge, tools, or prior concepts required to understand this video. If suitable for complete beginners, state: "None (Beginner-friendly)".]

Strict Rules:
- Base this strictly on the provided video information. Do NOT hallucinate or invent facts.
- If the context is in a language other than English, output the notes in clear English while preserving technical names.
- Do NOT output preamble, greetings, or meta-comments. Return only the Markdown content.
"""

CHAPTER_NOTES_PROMPT = """You are an expert educator and technical note-taking specialist.
Generate comprehensive, well-structured study notes for this specific YouTube chapter based ONLY on its transcript.

Chapter Number: {chapter_num}
Chapter Title: {chapter_title}
Timestamp: {timestamp_str}
Duration: {duration_str}

Chapter Transcript:
{transcript}

Generate the chapter notes strictly following this Markdown structure:

## Chapter {chapter_num}: {chapter_title}

**Timestamp:** {timestamp_str}
**Duration:** {duration_str}

### 1. Chapter Summary
[Write a clear, detailed explanation of the concepts discussed in this chapter. The summary should be understandable without watching the video again. Do not skip short chapters. If the chapter contains little information, provide a concise summary rather than inventing additional content.]

### 2. Key Concepts
[Explain each important concept introduced or discussed in this chapter.]
- **[Concept 1]**: [Explain in simple, clear language. Include relevant examples mentioned in the video.]
- **[Concept 2]**: [Explain in simple, clear language. Include relevant examples mentioned in the video.]

### 3. Important Details
[Explain processes, workflows, architectures, or methods discussed in this chapter.]
- [Explain processes or methods step-by-step.]
- [Include code snippets, terminal commands, mathematical formulas, or technical specifications when relevant.]
- [Preserve important facts, numbers, and concrete examples from the transcript.]

### 4. Practical Examples
[Include examples demonstrated in the video. If the video contains code, explain what the code does and how it works. If no practical example or code was demonstrated, explain practical real-world applications of the topic or state that no practical demonstration was presented in this chapter.]

### 5. Key Takeaways
[List 3 to 5 important points from this chapter.]
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

### 6. Important Terms
[Define the important terminology introduced in this chapter.]
- **[Term 1]**: [Definition in simple language.]
- **[Term 2]**: [Definition in simple language.]

Strict Rules:
- Never invent facts, examples, quotations, or explanations that are not supported by the transcript.
- If a detail is unclear or unavailable, explicitly state that it was not clear from the transcript.
- Preserve technical terminology, code, numbers, and examples accurately.
- If the transcript is in another language, produce clear study notes in English while faithfully maintaining technical terms, formulas, and code.
- Return pure Markdown without any wrapping explanation.
"""

CHAPTER_CHUNK_SUMMARY_PROMPT = """You are an expert technical note-taker analyzing a portion of a video chapter.
Read the following transcript segment from Chapter {chapter_num}: "{chapter_title}".
Extract all key concepts, technical explanations, code/commands/formulas, numbers, facts, and examples.
Remove conversational filler, jokes, or off-topic chatter.
Preserve all accurate technical details.

Transcript Segment:
{text}

Extracted Technical Information:
"""

FINAL_REVISION_PROMPT = """You are an expert educator and technical note-taking specialist.
Synthesize a comprehensive **Final Revision Section** based on all chapters of the video.

Video Title: {title}
All Chapter Notes and Summaries:
{all_chapters_summary}

Generate the final revision section strictly following this Markdown structure:

## Final Revision

### 1. Complete Video Summary
[A concise, comprehensive summary synthesizing the entire video across all chapters.]

### 2. Most Important Concepts
[The essential concepts that are critical to remember, with clear, high-yield explanations.]
- **[Concept 1]**: [Explanation]
- **[Concept 2]**: [Explanation]
- **[Concept 3]**: [Explanation]

### 3. Quick Revision Notes
[High-density bullet points for reviewing the video quickly before an interview, exam, or practical implementation.]
- [Quick bullet 1]
- [Quick bullet 2]
- [Quick bullet 3]
- [Quick bullet 4]
- [Quick bullet 5]

### 4. Glossary
[Alphabetical glossary of important terms and their definitions introduced across the entire video.]
- **[Term 1]**: [Clear definition]
- **[Term 2]**: [Clear definition]
- **[Term 3]**: [Clear definition]

### 5. Questions for Self-Assessment
[5 to 10 insightful questions based strictly on the actual video content to test comprehension.]
1. [Question 1]
2. [Question 2]
3. [Question 3]
4. [Question 4]
5. [Question 5]

#### Answers
[Detailed answers to each self-assessment question above.]
1. **Answer to Q1**: [Clear explanation based on video content]
2. **Answer to Q2**: [Clear explanation based on video content]
3. **Answer to Q3**: [Clear explanation based on video content]
4. **Answer to Q4**: [Clear explanation based on video content]
5. **Answer to Q5**: [Clear explanation based on video content]

Strict Rules:
- Base all questions, answers, and summaries strictly on the actual video topics.
- Never invent facts.
- Return pure Markdown.
"""

DETECT_CHAPTERS_PROMPT = """You are an expert video content analyzer.
The video titled "{title}" does not have official YouTube chapter markers.
Given the following timestamped outline sampled from the video transcript, divide the video into {target_count} logical, topic-based chapters.

Transcript Timestamped Outline:
{transcript_outline}

Respond with ONLY a valid JSON array of objects. Each object must have:
- "title": A concise, descriptive chapter title (string)
- "start_time": The start time in seconds (float or int)

Example format:
[
  {{"title": "Introduction to the Topic", "start_time": 0.0}},
  {{"title": "Core Architecture and Components", "start_time": 185.0}},
  {{"title": "Hands-on Implementation", "start_time": 420.0}}
]

Rules:
- The first chapter MUST start at 0.0.
- Timestamps must be sorted in strictly ascending order.
- Output ONLY valid JSON, with no preamble or markdown ticks.
"""

CHUNK_SUMMARY_PROMPT = """You are an expert at extracting information from parts of a larger video transcript.
Read the following transcript chunk and extract all important information, concepts, examples, and details.
Do not lose technical details. Remove conversational filler and off-topic discussion.
If the content is in a non-English language, translate and summarize key insights into English while preserving technical names.
Return the extracted information in a clean, readable format.

Transcript Chunk:
{text}
"""

FINAL_MERGE_PROMPT = """You are an expert educator, technical writer, and note-taking assistant.
You are given a series of summarized chunks from a video transcript.
Your task is to combine these into a single, cohesive, high-quality set of structured study notes.

Follow these rules:
1. Identify the main topic and create a suitable Title (`# Title`).
2. Provide a short `## Overview`.
3. Organize the content into logical sections (`##`) and subsections (`###`).
4. Extract important definitions, formulas, code concepts, processes, and examples.
5. Use bullet points, numbered lists, and tables to make it scannable.
6. Include a `## Key Takeaways` section at the end.
7. Format the entire output in Markdown.
8. Ensure the flow is logical and there is no disjointed text from the merging process.

Summarized Chunks:
{text}
"""

METADATA_FALLBACK_PROMPT = """You are an expert educator, technical writer, and note-taking assistant.
Audio transcripts/captions were not published for this video.
Your task is to synthesize comprehensive, high-quality study notes and curriculum breakdown from the video's official title, roadmap, chapter timestamps, and detailed description.

Video Information:
- Title: {title}
- Instructor / Channel: {channel}
- Duration: {duration}

Video Chapters & Timestamps:
{chapters}

Video Description & Topics:
{description}

Follow these instructions:
1. Create a suitable Title (`# {title}`).
2. Add a subtle notice block:
   > ℹ️ *Note: Captions/transcripts were unavailable for this video. These study notes were synthesized from the video's curriculum, timestamps, chapters, and syllabus.*
3. Provide an in-depth `## Overview` summarizing what this video covers.
4. If chapters/timestamps are present, create structured sections for each chapter (`## [Chapter Title]`), detailing the concepts and workflows taught in that section.
5. Extract and elaborate upon key definitions, concepts, and core educational takeaways from the syllabus and description.
6. Include a `## Key Takeaways` section at the end.
7. Format the entire output in Markdown.
"""

FALLBACK_CHAPTER_NOTES_PROMPT = """You are an expert educator and technical note-taking specialist.
Captions are unavailable for this video. Synthesize detailed, structured study notes for this specific chapter based on its title and the video syllabus.

Chapter Number: {chapter_num}
Chapter Title: {chapter_title}
Timestamp: {timestamp_str}
Duration: {duration_str}

Video Context and Syllabus:
{context}

Generate the chapter notes strictly following this Markdown structure:

## Chapter {chapter_num}: {chapter_title}

**Timestamp:** {timestamp_str}
**Duration:** {duration_str}

### 1. Chapter Summary
[Write a clear explanation of what is taught in this module based on the topic.]

### 2. Key Concepts
[Explain the primary concepts associated with {chapter_title}.]
- **[Concept 1]**: [Explanation]
- **[Concept 2]**: [Explanation]

### 3. Important Details
[Explain standard workflows, architectures, or methods relevant to this topic.]

### 4. Practical Examples
[Describe practical use cases or practical implementation patterns for this topic.]

### 5. Key Takeaways
- [Key point 1]
- [Key point 2]
- [Key point 3]

### 6. Important Terms
- **[Term 1]**: [Definition]
- **[Term 2]**: [Definition]

Strict Rules:
- Return pure Markdown without any wrapping explanation.
"""

QUICK_SUMMARY_PROMPT = """You are an expert AI summarizer focused on rapid, high-yield learning.
Generate a concise, crystal-clear Quick Summary for this educational video based strictly on its transcript.

Video Title: {title}
Duration: {duration}
Chapters Available: {chapters_list}

Transcript:
{transcript}

Generate your response in standard Markdown using the following structure:

# Quick Summary: {title}

> ⏱️ **Duration:** {duration} | **Source:** Video Transcript

## Executive Overview
[Provide a clear, 2-to-3 paragraph overview explaining the core theme, purpose, and significance of the video.]

## Core Concepts & Highlights
[List 4 to 6 crucial concepts or principles covered in the video with concise 1-sentence explanations.]
- **[Concept 1]**: [Explanation]
- **[Concept 2]**: [Explanation]
- **[Concept 3]**: [Explanation]

## Key Takeaways
[List 3 to 5 actionable bullet points that a learner should remember.]
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

## Chapter Roadmap & Highlights
[If chapters are present, provide a quick bullet list linking chapter names, timestamps, and the 1-line key idea from that chapter. If no chapters exist, provide a 3-part logical progression: Beginning, Core Content, Conclusion.]
- **[Timestamp] - [Chapter/Topic]**: [One-line summary]

Strict Rules:
- Prioritize speed, clarity, and conciseness.
- Do NOT hallucinate facts absent from the transcript.
- Return only Markdown with no conversational filler.
"""

DETAILED_NOTES_PROMPT = """You are a senior technical educator and academic curriculum architect.
Generate comprehensive, in-depth study notes for this video using the transcript.

Video Title: {title}
Duration: {duration}
Chapters Info:
{chapters_info}

Transcript:
{transcript}

Follow this detailed Markdown structure:

# Comprehensive Study Notes: {title}

## Video Overview & Conceptual Scope
[Thorough 2-3 paragraph explanation of the topic, foundational context, and practical relevance.]

### Key Objectives
- [Objective 1]
- [Objective 2]
- [Objective 3]

## Detailed Chapter-by-Chapter Analysis
[For each chapter or logical topic segment, write a detailed breakdown:]

### Chapter: [Chapter Name] ([Timestamp])
- **In-Depth Explanation:** [Detailed conceptual explanation]
- **Core Principles & Architecture:** [Technical concepts, steps, or mechanisms]
- **Practical Examples & Applications:** [Real-world use cases, code or design patterns]
- **Key Terminology:**
  - **[Term]**: [Definition and relevance]

## Synthesis & Key Takeaways
[Summarize the overarching lessons and mastery points.]
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

## Glossary of Essential Terminology
[Alphabetical list of the top technical terms discussed in this video with clear definitions.]
- **[Term 1]**: [Definition]
- **[Term 2]**: [Definition]

Strict Rules:
- Be thorough, pedagogical, and technically accurate.
- Base explanations directly on the transcript.
- If external domain context is helpful to explain standard industry concepts mentioned in the video, keep it strictly relevant and clearly integrate it.
- Return only the structured Markdown.
"""

RAG_QA_SYSTEM_PROMPT = """You are NoteTube AI, an expert educational teaching assistant grounded strictly in the video transcript.
Your job is to answer user questions about the video accurately, concisely, and factually using ONLY the provided transcript context chunks.

Strict Grounding Rules:
1. Answer using ONLY information present in the provided transcript context.
2. When referencing points made in the video, cite the relevant timestamps and chapter names in brackets, e.g. [03:45] or [Chapter 2: Core Concepts, 06:12].
3. If the transcript does NOT contain the answer, explicitly state:
   "Based on the provided video transcript, this topic is not mentioned or discussed."
   Do NOT guess, hallucinate, or fabricate facts or timestamps.
4. Keep answers concise, direct, and well-structured with bullet points or code snippets when helpful.
5. If general background helps clarify a transcript fact, clearly distinguish it: state "From the transcript: ..." versus "General note: ...".
"""

RAG_QA_USER_PROMPT = """Video Title: {title}

Retrieved Transcript Chunks:
{context_chunks}

User Question:
{question}

Provide your grounded answer with timestamp citations:"""

