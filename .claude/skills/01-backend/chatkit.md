---
name: chatkit-backend
description: OpenAI chat integration for Phase 3 chatbot. Use when building AI-powered todo assistant.
---

When building OpenAI chatbot backend:

1. **OpenAI client**:
   ```python
   from openai import OpenAI

   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   ```

2. **System prompt**:
   ```python
   SYSTEM_PROMPT = """You are a helpful todo assistant.
   Help users create, manage, and complete their tasks.
   Use the provided tools to interact with the todo database.
   Be concise and friendly."""
   ```

3. **Chat endpoint** (app/api/chat/route.ts):
   ```typescript
   import { OpenAI } from "openai";
   import { verifyJWT } from "@/lib/auth";

   const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

   export async function POST(req: Request) {
     const { message, history } = await req.json();
     const token = req.headers.get("authorization");
     const user = await verifyJWT(token);

     const completion = await openai.chat.completions.create({
       model: "gpt-4",
       messages: [
         { role: "system", content: SYSTEM_PROMPT },
         ...history,
         { role: "user", content: message }
       ]
     });

     return Response.json({
       reply: completion.choices[0].message.content
     });
   }
   ```

4. **Conversation history**:
   ```typescript
   const history = [
     { role: "user", content: "Add buy milk" },
     { role: "assistant", content: "Added task: Buy milk" }
   ];
   ```

5. **Environment**:
   ```
   OPENAI_API_KEY=sk-...
   ```
