# Technical Interview Task: Embeddable AI Customer Support Widget - Work Done

This document details the completed work for the Embeddable AI Customer Support Widget, addressing each core requirement and consideration outlined in the "Technical Interview Task" document.

## Loom Demo Videos

- [Demo Video 1](https://www.loom.com/share/043d8422b38e4b658230b7011a29049f?sid=ece64777-9ed4-428a-9ffc-d4fe0af53c29)
- [Demo Video 2](https://www.loom.com/share/043d8422b38e4b658230b7011a29049f?sid=ece64777-9ed4-428a-9ffc-d4fe0af53c29)
- [Demo Video 3](https://www.loom.com/share/503870836f474ad9aecf4e06ff4b425a?sid=4668a988-bef3-4f45-a152-3be41908198d)
- [Demo Video 4](https://www.loom.com/share/74b407385e2b40e282fea9176f37d496?sid=3ce0fdf5-d610-4bfb-b338-130f692a596e)

## Setup Project

### Backend Setup

1. Use uv to install dependencies(`uv sync`) and set up the backend.
2. Set up a PostgreSQL DB instance.
3. Fill out environment variables based on .env.example. Key variables include:

MODEL_API_KEY=your_gemini_api_key
MODEL_NAME=gemini-2.0-flash
DB_USER=...
DB_PASSWORD=...

Then finally run `python3 app.py`, it will create the table automatically and run the server.

`uvicorn app:app --host 0.0.0.0 --port 8000 --reload` command for live debugging

### Frontend Setup

1. Open index.html from the Frontend folder in your browser.
2. Ensure the environment configuration is set in the embedded script:

window.ChatbotWidgetConfig = {
  backendBaseUrl: "http://localhost:8000",
  title: "Embedded Chatbot",
  hostUrl: "https://company-website.com",
  hostDescription: "Short description of company",
  ...
};

You will need service credentials for Email JS, Google OAuth etc(As mine are private), Provided are the links to get them:

1. Email JS(Email Client): https://dashboard.emailjs.com
2. Google OAuth(Authentication): https://developers.google.com/identity/protocols/oauth2
3. Gemini API Key(Chatbot Response Generation on Scale): https://ai.google.dev/gemini-api/docs/api-key
4. Sentry(Issue + Error Tracking): https://sentry.io After creating account + project, goto "Project -> settings -> Client Keys" to get the DSN key.
5. PineCone(VectorDB): https://www.pinecone.io
6. FireCrawl(AI Powered Web Scrapping): https://www.firecrawl.dev/
7. VoyageAI(Embedding Model): https://www.voyageai.com/
8. Calendly: Get the your scheduled meeting post URL
9. DeepSeek Model(Good For Information Extraction, Reasoning + Cost): https://platform.deepseek.com

Then open the frontend by copy pasting the index.html file path into the browser e.g  "/Embeddable-AI-Customer-Support-Widget/Frontend/index.html"
That’s it — the chatbot should be up and running on your local machine.

## 1. Embeddable Widget

**Requirements Met:**

- **Create a lightweight, embeddable JavaScript widget that works across different platforms:** Fulfilled. The widget is integrated using a simple script tag, making it embeddable across various platforms like Wix, WordPress, and Next.js.
- **Should be easily integrated with a simple script tag or component:** Fulfilled. Integration is achieved by including a `<script>` tag with `window.ChatbotWidgetConfig` for configuration.
- **Responsive design that works on mobile and desktop:** Fulfilled. The chatbot is described as highly professional and responsive to all screen sizes.
- **Customizable styling to match different websites:** Fulfilled. Styling (colors), title, backend URL, and other parameters are customizable through the `ChatbotWidgetConfig` object in the script tag.
- **Minimal impact on host website performance:** Implicitly addressed by using a lightweight JavaScript approach and scoped CSS.

**Demo**

    `<script>`
      window.ChatbotWidgetConfig = {
        colors: {
          primary: "#009688",
          primaryDark: "#00695c",
          accent: "#b2dfdb",
        },
        // Email Configuration
        emailJsUserId: "",
        emailJsServiceId: "",
        emailJsSupportTemplateId: "",
        emailJsUserTemplateId: "",
        // Title of Chatbot
        title: "Embedded Chatbot",
        // Backend URL for our service
        backendBaseUrl: "http://localhost:8000",
        // Google Authentication
        googleClientId: "",
        // Target Company Data
        hostUrl: "https://crumblcookies.com/",
        hostDescription: "Crumbl Cookies is a cookie company that sells cookies",
        calendlyUrl: "",
      };
    `</script>`

**Implementation Details:**

- The chatbot uses scoped CSS, ensuring that its styling only affects the parent-defined root div and avoids conflicts with the host website's CSS.

## 2. AI Chat Interface

**Requirements Met:**

- **Real-time chat interface with the AI:** Fulfilled. The chatbot provides a real-time chat experience.
- **AI should provide contextual responses about the company/website:** Fulfilled. Pinecone VectorDB to index specialized data, FireCrawl scrapes the provided URLs and then are indexed by PineCone to provide accurate context. The AI (Google Gemini Flash 2.0 with Google Search support) uses the provided `hostUrl` and `hostDescription` to gather real-time information about the company for contextual responses.
- **Support for rich responses (buttons, forms, calendar pickers):** Fulfilled. The chatbot supports in-built calendar (Calendly scheduling) and forms (human handoff), and has some support for Markdown.
- **Chat history within the session:** Fulfilled. Chat history within the session is retained.
- **Professional, clean UI/UX:** Fulfilled. The chatbot is described as highly professional and responsive

**Demo Screenshots:**

<table style="width: 100%; height: 50%;">
  <tr>
    <td><img src="image/main/1749929994017.png" alt="1749929994017" style="width: 100%; height: 100%;"> Desktop View</td>
    <td><img src="image/readme/1750011942275.png" alt="1750011942275" style="width: 100%; height: 100%;">Mobile View</td>
  </tr>
</table>

**Implementation Details:**

- All user sessions and their chat histories are stored in the backend database.

## 3. Action 1: Google Calendar Integration (Required)

**Requirements Met:**

- **Connect to Google Calendar API to pull real-time availability:** Fulfilled, but with a strategic alternative. Instead of directly integrating with Google Calendar API, Calendly's iFrame solution was chosen, which inherently handles real-time availability.
- **Display available time slots to users in a user-friendly format:** Fulfilled by Calendly's iFrame, which provides a visual calendar for selecting days
- **Allow users to book appointments directly through the widget:** Fulfilled by Calendly's iFrame integration
- **Create calendar events with Google Meet links automatically:** Fulfilled by Calendly's functionality.
- **Send confirmation emails with calendar invites:** Fulfilled by Calendly's functionality
- **Handle timezone conversions properly:** Fulfilled by Calendly's built-in timezone management.

**Demo Screenshots:**

<!-- BEGIN COLLAGE 1 -->

<table>
  <tr>
    <td><img src="image/main/1749929072956.png" alt="1749929072956" style="width: 100%; height: 50%;"></td>
    <td><img src="image/main/1749929274951.png" alt="1749929274951" style="width: 100%; height: 50%;"></td>
    <td><img src="image/main/1749929286416.png" alt="1749929286416" style="width: 100%; height: 50%;"></td>
    <td><img src="image/main/1749929297689.png" alt="1749929297689" style="width: 100%; height: 50%;"></td>
  </tr>
</table>
<!-- END COLLAGE 1 -->

**Implementation Details:**

- Calendly was chosen as a ready-to-use solution via an iFrame, eliminating the need to build Google Calendar API integrations from scratch and leveraging Calendly's proven user experience and features.
- Appointment rescheduling and slot availability management are handled directly from the Calendly website.

## 4. Action 2: Human Handoff (Required)

**Requirements Met:**

- **When user requests to talk to a human, show a form to collect:**

  - Name (required)
  - Email (required)
  - Phone (optional)
  - Message/Issue description (required)
  - Priority level (Low/Medium/High/Urgent)
  - **All form requirements are met within the application.**
- **Send email notification to support team with form details:** Fulfilled using EmailJS.
- **Send auto-confirmation email to the user:** Fulfilled using EmailJS.
- **Generate a support ticket ID for tracking:** Fulfilled. A support ticket ID is generated for tracking, as shown in the email example and all support tickets along with their status(Open|Closed|Inprogress) saved in the database for tracking.

**Demo Screenshots:**

<!-- BEGIN COLLAGE 2 -->

<table>
  <tr>
    <td><img src="image/main/1749929315036.png" alt="1749929315036" style="width: 100%; height: 50%;"></td>
    <td><img src="image/main/1749929328159.png" alt="1749929328159" style="width: 100%; height: 50%;"></td>
  </tr>
</table>
<!-- END COLLAGE 2 -->

**Implementation Details:**

- A user issue tracking system is built into the backend to conveniently manage user issues.
- EmailJS is used for sending email notifications to the support team and auto-confirmations to the user.

## 5. Interaction Logging (Required)

**Requirements Met:**

- **Log all conversations to Supabase|Postgres database:** Fulfilled. All user sessions and messages are stored in the backend databases.
- **Track user sessions, messages, and actions taken:** Fulfilled. Stored sessions include information regarding bookings and human handoff forms.
- **Store metadata like timestamps, user info, conversation outcomes:** Fulfilled. This information is part of the stored sessions.
- **Basic analytics on conversation volume and success rates:** Fulfilled. Information is processed daily via a cron job to get the volume of conversations and success rates and furthermore using sentry to track all API bugs, errors etc in real time

**Demo Screenshots:**

<table>
  <tr>
    <td><img src="image/readme/1749976763812.png" alt="1749976763812" style="width: 100%; height: 50%;">Sentry</td>
    <td><img src="image/readme/1749976821435.png" alt="1749976821435" style="width: 100%; height: 50%;">Analytics</td>
  </tr>
</table>

**Implementation Details:**

- PostgreSQL is the chosen database for logging interactions in local development but Supabase provides instance of PostgreSQL in production so wouldn't be an issue. Furthermore Sentry is chosen for error and issues logging of the APIs.

## Technical Stack Requirements

**Backend:**

- **Database:** PostgreSQL 14, PineCone VectorDB
- **LLM:** Google Gemini Flash 2.0 (via OpenRouter API, with Google Search Support enabled), Deep Seek.
- **APIs:** Email service (EmailJS[Used in Frontend]), Calendly (instead of Google Calendar API).
- **Framework:** FAST API with Python.
- **Other:** Alembic(Data Migrations), Sentry(Issues Logging), Rate Limiter, Google Authentication, Ruff(Python Linter), Pydantic(Typing Within Python), SQL Alchemy(ORM), Voyage AI(Embedding Model), FireCrawl AI(AI Powered WebScrapper).

**Frontend:**

- **Widget:** Vanilla JS.
- **Styling:** Scoped CSS.
- **Build:** Bundling for easy distribution.
- **Other:** EmailJS, Calendly, Google Authentication, Markdown parser, Emoji Picker, HTML.

## Architecture Considerations for Future

- **Appointment Rescheduling:** Already handled by Calendly, which offers API support for this.
- **Internal Database Queries:** Easily attachable using SQL Alchemy ORM with Alembic migrations or via API calls. Pinecone VectorDB attached for vector stores/Large Knowledge base.
- **Live Agent Handoff:** A flag or quick email notification to a human agent, with a real-time websocket connection if availability is confirmed, can facilitate seamless transition.
- **Multi-language Support:** Easily done with the prompt.
- **Advanced Analytics:** Basic analytics are implemented, with potential for improvement on the analytics module or integration with tools like Google Analytics. Sentry  also used for advanced issue related analytics.

**Overall Architecture:**

- The backend infrastructure is built on a "screaming architecture," emphasizing modularity and ease of modification. Furthermore OOP(Object Oriented Programming) is being utilized for service modules which can allow us for easy import of modules in other services and Functional Programming for REST APIs.
- The chatbot is designed to be highly modular, allowing most changes to be handled by adjusting frontend parameters, with the backend automatically adapting.

## Deliverables

- **Widget Implementation:**

  - Embeddable JavaScript file: Provided through the script tag integration.
  - Demo HTML page: Implied by the integration instructions.
  - Basic customization options: Covered by the `ChatbotWidgetConfig`.
- **Backend API:**

  - RESTful API endpoints for chat, calendar, and support requests: Implemented with FAST API.
  - Google Calendar integration for availability and booking: Fulfilled through Calendly integration
  - Email notification system for support requests: Implemented using EmailJS.
  - Database operations for logging interactions: Handled with Postgres, PineCone and Sentry.
  - Web Scrapping: Handled by Firecrawl AI
- **Database Setup:**

  - PostgreSQL Native project with proper tables for conversations, bookings, and support requests: Implemented except for bookings as Calendly is handling it automatically.
  - Vector embeddings setup for AI context: PineCone VectorDB(Large Knowledge Base) + Google Search with Gemini 2.0(Short Real Time Knowledge Base)

  Creating a revision: `alembic revision -m "Description of the revision"`
  Upgrading To latest Postgres Migration: `alembic upgrade head`

![Scrape+Purify+Ingest+Index-into-pinecone](image/readme/1750245003676.png)

- **Documentation:**

  - Integration guide: Provided in the `script` tag example.
  - API documentation: Provided by FAST API[Use the FAST API interactive docs] and also in the commented code.

  ![1749978348993.png](image/readme/1749978348993.png)

  <table>
      <tr>
        <td><img src="image/readme/1749977650402.png" alt="Image 2" style="width: 100%; height: 50%;"></td>
        <td><img src="image/readme/1749977669087.png" alt="Image 3" style="width: 100%; height: 50%;"></td>
      </tr>
    </table>
  - Setup instructions for Google Calendar and email services: Covered by the Calendly URL and EmailJS credentials in the configuration.

## Evaluation Criteria

- **Technical Implementation (40%):**

  - Clean, well-organized code: Implied by the "screaming architecture", OOP for services + Functional Programming and choice of frameworks (FAST API, SQL Alchemy).
  - Proper error handling: Sentry is installed in the backend for real-time system failure updates and bug tracking.
  - Security best practices: Google OAuth, Rate limiting, CORS configuration, token-based authentication for requests, and payload limits are implemented.
  - Widget integration works smoothly: Confirmed by the description of the embeddable and customizable widget
- **Feature Completeness (40%):**

  - Google Calendar integration works correctly: Fulfilled via Calendly.
  - Human handoff form and email system functions properly: Fulfilled using EmailJS and the in-built issue tracking.
  - entry.
  - AI provides relevant responses: Fulfilled by PineCone VectorDB and Gemini 2.0 with Google Search capabilities.
- **User Experience (20%):**

  - Intuitive and responsive interface: Confirmed by the description and provided screenshots
  - Smooth booking and handoff flows: Demonstrated by the Calendly integration and human handoff form process.
  - Professional appearance and behavior: Confirmed by the description and visual evidence.
  - Good documentation for integration: Provided through the script tag example.

## Questions to Consider

1. **How will you handle widget styling conflicts with host websites?**

   - Handled by using scoped CSS, where the parent-defined div is considered the root, ensuring only its particular CSS is modified.
2. **What happens when Google Calendar API is unavailable?**

   - Not directly applicable as Calendly is used. Calendly's service availability would be the concern, and it's a robust, proven solution.
3. **How will you manage conversation context for the AI?**

   - Chat history within the session is retained. The AI leverages Google Gemini Flash 2.0 with Google Search support and is provided with `hostUrl` and `hostDescription` for real-time contextual information. Alongside we are using Pinecone VectorDB to get specialized indexed data.
4. **What security measures will you implement?**

   - Google OAuthentication, Rate limiting for API calls, CORS configuration, token-based authentication for requests, and payload limits are implemented. Sentry is also used for real-time system failure updates and bug tracking.
5. **How will you handle different timezones for calendar bookings?**

   - Handled inherently by Calendly's built-in functionality

## Future Considerations

Shifting Calendly and Email notification systems to backend via APIs for enhanced security, but need to find a way on how to automtically get calendly API key and email service credentials from the user. So we can stop people from getting their hands on even public API's and URLs.
