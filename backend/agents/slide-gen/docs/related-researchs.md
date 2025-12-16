关于利用大模型（LLM）和多模态大模型（VLM）进行演示文稿（Slide/PPT）制作，最新的研究趋势已经从简单的“文本摘要生成大纲”向**“Agent智能体协作”**、**“代码生成渲染”**以及**“多模态排版布局”**转变。

以下为您精选的5篇最新（2024-2025）代表性工作，涵盖了计算机视觉、自然语言处理等领域的顶会（如ACL, EMNLP, ICLR等）及最新arXiv前沿论文，均包含Benchmark（基准测试）或重要数据集。

###1. Paper2Slide: A Multi-Agent Framework for Automatic Scientific Slide Generation* **来源/时间**：2025 (OpenReview, ICLR/NeurIPS Submission)
* **核心亮点**：**学术论文转PPT的专用Benchmark**
* **主要内容**：
* **任务**：专注于将科研论文（PDF/Latex）自动转换为专业的学术汇报PPT。
* **方法 (SlideGen)**：提出了一个多智能体（Multi-Agent）框架，包含“大纲生成”、“内容映射”、“图表提取”和“布局规划”等多个Agent协作。它不仅仅是总结文本，还能把论文里的图表（Figures）准确地放置在对应的Slide页面上。
* **Benchmark (Paper2Slide)**：构建了一个包含200对高质量“论文-PPT”的数据集。
* **评价指标**：提出了一套综合评估协议，从叙事质量、事实覆盖率、视觉可读性等方面打分。



###2. PPTC / PPTC-R: Evaluating Large Language Models for PowerPoint Task Completion* **来源/时间**：**ACL 2024 Findings / EMNLP 2024 Findings**
* **核心亮点**：**API调用与操作鲁棒性测试**
* **主要内容**：
* **任务**：不同于“从零生成”，这篇工作关注LLM如何通过**API调用**来操作PowerPoint软件（如“把第三页的标题改成红色”、“插入一张表格”）。
* **Benchmark (PPTC & PPTC-R)**：提出了包含数百个多轮对话Session的基准测试，用来评估LLM是否真能“听懂”用户的修改指令并正确执行PPT API。PPTC-R进一步测试了模型面对模糊指令或软件版本更新时的**鲁棒性**。
* **意义**：这是目前评估LLM作为“PPT Copilot（助手）”能力的权威基准之一。



###3. PPTAgent: Generating and Evaluating Presentations Beyond Text-to-Slides* **来源/时间**：arXiv 2025 (近期热门工作)
* **核心亮点**：**基于参考模板的逆向分析与生成**
* **主要内容**：# VN-Check: A Fine-Grained Visual-Narrative Alignment Framework for Long-Form Document-to-Presentation

**Research Track:** NLP / Multi-Modal Learning (e.g., ACL, NeurIPS Datasets & Benchmarks)  
**Core Problem:** "Hallucination" and "Dissonance" in Multi-Modal Generation.

---

## 1. Abstract & Motivation

The previous proposal ("Paper-to-Slide") was a system-building task. This proposal pivots to a **fundamental scientific problem**: **Cross-Modal Consistency in Long-Context Generation**.

When Large Language Models (LLMs) and Diffusion Models collaborate to transform a 10-page document into a 10-slide deck, they suffer from **"Information Loss"** and **"Visual-Narrative Dissonance"**.
*   **Example of Dissonance:** The text discusses "Decreasing Latency", but the generated chart shows an upward trend (because the image generator didn't understand the axis).
*   **Example of Information Loss:** The slide bullet points capture the *introduction* of a paragraph but miss the *critical nuance* at the end.

This research proposes **VN-Check (Visual-Narrative Check)**, a diagnostic framework and benchmark to quantify and mitigate these errors. We treat "Slide Generation" not as an engineering end-goal, but as a **complex reasoning testbed** for long-context multi-modal agents.

---

## 2. Core Research Questions (RQs)

1.  **RQ1 (Granularity):** Can we automatically detect when a generated image implies a sentiment or fact that contradicts the accompanying bullet points? (e.g., A "happy" stock photo for a slide about "Market Crash").
2.  **RQ2 (Attention Alignment):** Does the "Visual Saliency" of the slide (where the eye looks first) align with the "Semantic Importance" of the source text? (i.e., Is the most important point visually the biggest?).
3.  **RQ3 (Compression Fidelity):** What is the "Bit-Rate" of the summarization? How much semantic information is lost when moving from `Paragraph -> Bullet Point -> Icon`?

---

## 3. Proposed Methodology

We will upgrade the current `slide-gen` agent into an **Evaluation Harness**.

### 3.1 Dataset Construction: `Doc2Slide-Entailment`
We will construct a dataset of (Source Segment, Slide Element) pairs annotated with **Entailment Labels**:
*   **Entailment:** The slide element faithfully represents the source.
*   **Contradiction:** The slide element (text or image) contradicts the source.
*   **Neutral/Hallucination:** The slide adds information not present in the source.

### 3.2 The `VN-Critic` Module (The Novel Contribution)
Instead of just generating slides, we develop a specialized **VLM-based Reward Model** trained to detect dissonance.

*   **Input:** A rendered slide image (from `renderer/image_exporter.py`) + Original Source Text snippet.
*   **Mechanism:**
    1.  **Region-of-Interest (ROI) Extraction:** Use an Object Detector to find charts, icons, and text blocks.
    2.  **Cross-Modal grounding:** Use a VLM (e.g., CLIP, SigLIP, or GPT-4o) to compute the cosine similarity between the *visual embedding* of the ROI and the *text embedding* of the source concept.
    3.  **Dissonance Score:** If `Similarity(Visual, Text) < Threshold`, flag as dissonance.

### 3.3 Experiment: "Self-Correction via Dissonance Minimization"
We will modify the `slide-gen` workflow (in `agent/graph.py`):
1.  **Generate** a slide draft.
2.  **Measure** Dissonance Score using `VN-Critic`.
3.  **Optimize**: If Dissonance is high, the agent must *regenerate* the image prompt or *rewrite* the bullet points to maximize alignment.
4.  **Hypothesis**: This closed-loop approach reduces hallucination rates by 40% compared to open-loop generation.

---

## 4. Why This Fits a Top Conference

*   **Scientific Value:** It addresses **Safety and Trustworthiness** in GenAI. A slide deck that hallucinates data is dangerous.
*   **Metric Contribution:** It proposes a new metric (Visual-Narrative Alignment Score) rather than just a tool.
*   **Generalizability:** The findings apply to *any* document-to-visual task (Posters, Infographics, UI Design), not just slides.

---

## 5. Implementation Roadmap for `slide-gen`

1.  **Instrumentation:** Modify `src/agent/nodes.py` to save not just the final slide, but the "intermediate reasoning" (the mapping between source text and generated slide content).
2.  **Critic Agent:** Implement `src/agent/critic.py` containing the `VNCritic` class using a VLM API.
3.  **Benchmark Mode:** Create a script `run_benchmark.py` that runs the agent on 50 diverse papers and logs the Dissonance Scores.


* **方法**：即许多现有的工具生成的PPT很丑、结构单一。PPTAgent 模仿人类的制作流程：先“看”（分析）高质量的参考模板，提取设计Schema（配色、布局模式），然后根据内容填空。
* **Benchmark (PPTEval)**：提出了一个名为**PPTEval**的评估框架，利用多模态大模型（如GPT-4V）从**内容（Content）、设计（Design）、连贯性（Coherence）**三个维度对生成的PPT进行自动评分，比传统的文本相似度指标（ROUGE）更符合人类直觉。



###4. AutoPresent: Designing Structured Visuals from Scratch* **来源/时间**：arXiv 2025
* **核心亮点**：**通过写代码（Code-to-Slide）来画PPT**
* **主要内容**：
* **思路**：直接让大模型生成PPT文件很容易出错（格式乱）。AutoPresent 提出让LLM生成**Python代码**（使用专门设计的SlidesLib库），通过执行代码来精确控制PPT的每一个元素、坐标和样式。
* **Benchmark (SlidesBench)**：包含数千条“指令-代码-PPT”数据对，测试模型将自然语言指令转化为精确布局代码的能力。
* **模型**：发布了一个基于Llama-8B微调的**AutoPresent**模型，在布局控制力上接近GPT-4o。



###5. Enhancing Presentation Slide Generation by LLMs with a Multi-Staged End-to-End Approach* **来源/时间**：**INLG 2024** (自然语言生成国际会议)
* **核心亮点**：**多阶段叙事优化**
* **主要内容**：
* **痛点**：解决现有工具“只贴文字，没有讲故事逻辑”的问题。
* **方法**：提出了一个端到端的多阶段生成模型。第一阶段利用LLM进行长文档的深度理解和叙事结构提取；第二阶段利用VLM进行图文匹配和多模态排版。
* **贡献**：证明了将“内容规划”与“视觉呈现”分阶段处理，比直接让GPT-4“一步到位”生成的PPT质量更高，更符合演讲逻辑。


