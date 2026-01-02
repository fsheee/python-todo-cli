---
name: chatkit-frontend
description: React chat UI for OpenAI chatbot. Use when building chatbot interface.
---

When building chat UI:

1. **Chat component** (components/ChatBox.tsx):
   ```tsx
   "use client";
   import { useState } from "react";

   interface Message {
     role: "user" | "assistant";
     content: string;
   }

   export function ChatBox() {
     const [messages, setMessages] = useState<Message[]>([]);
     const [input, setInput] = useState("");
     const [loading, setLoading] = useState(false);

     const sendMessage = async () => {
       if (!input.trim()) return;
       setLoading(true);

       const userMsg = { role: "user" as const, content: input };
       setMessages(prev => [...prev, userMsg]);
       setInput("");

       const res = await fetch("/api/chat", {
         method: "POST",
         body: JSON.stringify({
           message: input,
           history: messages
         })
       });
       const data = await res.json();

       setMessages(prev => [...prev, {
         role: "assistant",
         content: data.reply
       }]);
       setLoading(false);
     };

     return (
       <div className="chat-container">
         <div className="messages">
           {messages.map((m, i) => (
             <div key={i} className={m.role}>
               {m.content}
             </div>
           ))}
         </div>
         <div className="input-area">
           <input
             value={input}
             onChange={e => setInput(e.target.value)}
             onKeyDown={e => e.key === "Enter" && sendMessage()}
             placeholder="Ask me to manage your tasks..."
           />
           <button onClick={sendMessage} disabled={loading}>
             {loading ? "..." : "Send"}
           </button>
         </div>
       </div>
     );
   }
   ```

2. **Message styling**:
   ```css
   .user { background: #e3f2fd; padding: 10px; margin: 5px; border-radius: 8px; }
   .assistant { background: #f5f5f5; padding: 10px; margin: 5px; border-radius: 8px; }
   .input-area { display: flex; gap: 10px; margin-top: 10px; }
   ```

3. **Auto-scroll to bottom**:
   ```typescript
   const bottomRef = useRef(null);
   useEffect(() => {
     bottomRef.current?.scrollIntoView({ behavior: "smooth" });
   }, [messages]);
   ```

4. **Quick actions**:
   ```tsx
   <div className="quick-actions">
     <button onClick={() => setInput("Show my tasks")}>Show tasks</button>
     <button onClick={() => setInput("Add task")}>Add task</button>
   </div>
   ```
