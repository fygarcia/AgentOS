## **Product Requirements Document (PRD)**

### **Feature: Persistent "File-System-as-State" Memory Architecture**

**Target System:** Python-based AI Assistant **Reference Architecture:** OpenClaw (Clawdbot/Moltbot)

### **1\. Executive Summary**

This feature implements a "conscious" memory system that allows the AI agent to maintain state across independent execution sessions. Unlike standard RAG (which retrieves static documents), this system treats local files as **Mutable Working Memory**. The agent must be able to read its current status (NOW.md) and recent history (LOG.md) before every action, and write to them to "save" its progress.  
**Core Philosophy:** The file system is the agent's RAM. If the process is killed and restarted, the agent reads the files and resumes exactly where it left off.

### **2\. System Architecture**

#### **2.1 The Three-Layer Memory Model**

The memory system is divided into three distinct layers based on retrieval frequency and mutability.

| Layer | Component | Implementation | Function |
| :---- | :---- | :---- | :---- |
| **Hot (Working)** | NOW.md | Local Markdown File | Stores the *current* objective, immediate next steps, and active blockers. Read/Written on almost every turn. |
| **Warm (Episodic)** | LOG.md | Local Markdown File | A chronological journal of the last \~20 actions, tool outputs, and user corrections. Read every turn; Append-only. |
| **Cold (Semantic)** | chroma\_db/ | Vector Database | Massive archive of past conversations and facts. Only accessed via explicit tool call (search\_memory). |

#### **2.2 Directory Structure**

The application must initialize and maintain the following structure in the user's workspace:  
`/workspace_root`  
`│`  
`├── /memory`  
`│   ├── NOW.md          # The "Attention" file`  
`│   ├── LOG.md          # The "Short-term History" file`  
`│   └── facts.json      # Structured user preferences (kv-store)`  
`│`  
`├── /directives`  
`│   ├── AGENTS.md       # Core identity & operating rules (Read-only)`  
`│   └── SKILLS.md       # Available capabilities documentation`  
`│`  
`└── /chroma_db          # Vector store persistence directory`

### **3\. Functional Requirements**

#### **3.1 The Context Injection Pipeline (The "Read" Loop)**

**Trigger:** Executed *before* every API call to the LLM. **Owner:** Orchestrator (Python Main Loop)  
**Workflow:**

1. **Intercept User Message:** Receive string input\_text.  
2. **Load Static Context:** Read content of directives/AGENTS.md.  
3. **Load Dynamic Context:**  
   * Read memory/NOW.md. If empty, initialize with "Status: Idle".  
   * Read memory/LOG.md. If file size \> 50KB, trigger *Compaction Protocol* (see 3.4).  
4. **Assemble System Prompt:** Concatenate these inputs into the final payload.

**Requirement:** The final prompt sent to the LLM must strictly follow this structure:  
`<SYSTEM_PROMPT>`  
`{AGENTS.md Content}`

`=== CURRENT MENTAL STATE (Do not ignore) ===`  
`You are currently working on:`  
`{NOW.md Content}`

`=== RECENT ACTIVITY LOG ===`  
`{LOG.md Content}`  
`</SYSTEM_PROMPT>`

`<USER_INPUT>`  
`{input_text}`  
`</USER_INPUT>`

#### **3.2 The State Management Tools (The "Write" Loop)**

The LLM must be equipped with specific tools to manipulate these files. These are **Atomic Actions**.  
**Tool 1: update\_status**

* **Purpose:** Overwrite NOW.md to change the current focus.  
* **Trigger:** LLM decides it has finished a step or needs to pivot.  
* **Python Signature:**  
  `def update_status(new_status_text: str, next_step: str) -> str:`  
      `"""`  
      `Overwrites NOW.md. Use this to keep track of your current goal.`  
      `Format: # Current Goal: {new_status_text} \n- Next: {next_step}`  
      `"""`

**Tool 2: log\_activity**

* **Purpose:** Append a new entry to LOG.md.  
* **Trigger:** After every tool execution or significant reasoning step.  
* **Python Signature:**  
  `def log_activity(entry_type: str, content: str) -> str:`  
      `"""`  
      `Appends to LOG.md with timestamp.`  
      `entry_type: 'TOOL_USE', 'THOUGHT', or 'USER_FEEDBACK'`  
      `"""`

**Tool 3: recall\_memory**

* **Purpose:** Search the Cold (Vector) memory.  
* **Trigger:** When NOW.md and LOG.md do not contain necessary context.  
* **Python Signature:**  
  `def recall_memory(query: str) -> str:`  
      `"""`  
      `Embeds query and searches ChromaDB for top 3 relevant chunks.`  
      `"""`

#### **3.3 The "Self-Annealing" Logic**

**Condition:** If an error occurs (Python Exception or API Failure). **Workflow:**

1. The Orchestrator catches the exception.  
2. The Orchestrator **automatically** writes the error trace to LOG.md.  
3. The Orchestrator invokes the LLM with a specialized "Recovery Prompt":"You encountered an error. Read the last entry in LOG.md. Update NOW.md with a plan to fix this, then execute the fix."

#### **3.4 The Compaction Protocol (Garbage Collection)**

**Condition:** LOG.md exceeds defined token/size limit (e.g., 50KB). **Workflow:**

1. **Read:** Orchestrator reads full LOG.md.  
2. **Summarize:** Send to LLM with prompt: "Summarize the key events and outcomes from this log into a coherent narrative."  
3. **Archive:** Store the summary in chroma\_db (Cold Memory).  
4. **Flush:** Clear LOG.md and write the summary as the first entry (to maintain continuity).

### **4\. Implementation Specifications (Python)**

#### **4.1 Orchestrator Pseudocode**

This is the logic flow your coding assistant needs to implement.  
`class AgentOrchestrator:`  
    `def run_turn(self, user_input):`  
        `# 1. READ PHASE`  
        `now_state = self.read_file("memory/NOW.md")`  
        `log_history = self.read_file("memory/LOG.md")`  
          
        `# 2. PROMPT CONSTRUCTION`  
        `system_prompt = f"""`  
        `You are an autonomous agent.`  
        `RULES: directives/AGENTS.md`  
          
        `YOUR CURRENT STATUS:`  
        `{now_state}`  
          
        `YOUR RECENT HISTORY:`  
        `{log_history}`  
        `"""`  
          
        `# 3. LLM EXECUTION`  
        `response = llm.generate(`  
            `system_prompt=system_prompt,`   
            `user_input=user_input,`  
            `tools=[update_status, log_activity, recall_memory]`  
        `)`  
          
        `# 4. EXECUTION PHASE`  
        `if response.tool_calls:`  
            `for tool in response.tool_calls:`  
                `result = execute_tool(tool)`  
                `# AUTO-LOGGING: System automatically logs tool results`  
                `self.append_to_log(f"Tool {tool.name} executed. Result: {result}")`  
                  
        `return response.content`

#### **4.2 System Prompt Directives**

You must add this specific instruction block to your AGENTS.md (or equivalent system prompt) to force the behavior:  
**MEMORY MANAGEMENT PROTOCOL**

1. **Check NOW.md first**: Before answering, look at your "Current Status". Is this a continuation of a previous task?  
2. **Update NOW.md frequently**: If you change your plan or finish a step, you MUST call update\_status. Do not keep your plan in your "head" (context window); write it to the file.  
3. **Consult LOG.md**: If the user says "it didn't work", check the log to see specifically what you tried last.

### **5\. Success Criteria & Validation**

To verify the implementation is correct, run these "State Persistence Tests":

1. **The "Amnesia" Test:**  
   * Give the bot a complex task (e.g., "Research topic X and outline a blog post").  
   * Wait for it to finish the research step.  
   * **Kill the python process completely.**  
   * Restart the process and say "Continue."  
   * *Success:* The bot reads NOW.md, sees it finished research, and immediately starts outlining without asking "What was I doing?"  
2. **The "Correction" Test:**  
   * Tell the bot: "My API key is 12345."  
   * The bot should call log\_activity or a preference tool.  
   * Chat for 50 turns (flushing the context window).  
   * Ask: "What is my API key?"  
   * *Success:* The bot calls recall\_memory (Vector DB) or scans the compacted log to find "12345".