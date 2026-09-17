# SupportAI

Support teams often answer the same questions repeatedly. SupportAI helps turn their past solutions into reusable answers.

It finds similar problems in solved support cases and drafts answers to frequently asked questions (FAQs). A person checks each draft alongside the original cases, edits it, and decides whether to approve it.

## See it in action

Three customers paid successfully but couldn't find their receipts. Support found one in spam, confirmed another email arrived late, and resent the third.

Those solutions become one draft: **“My payment went through. Where is my receipt?”** It explains what to check and when to ask for help—without repeating a confirmed payment.

![Receipt FAQ draft beside three original cases, with options to edit, approve, or reject it](docs/images/faq-detail.png)

*Both screenshots use made-up cases and fixed demo results, not AI-generated answers. “Confidence” measures how similar the cases are, not answer accuracy.*

You can also compare cases side by side to understand why they belong together.

![Color grid comparing six cases, with two receipt problems and their solutions shown side by side](docs/images/similarity-matrix.png)

*Two related receipt problems, solved in different ways.*

## What to know

This is an early version for running on your own computer, not a finished support service.

- Drafts, edits, and review decisions are temporary. Restarting the service, reloading the page, or generating new drafts can clear work.
- Approving an answer only marks it as reviewed. Export and publishing are not available.
- Cases need specially prepared files; there is no automatic connection to support tools.
- There is no login or access protection. Answer quality, case grouping, and speed have not been formally evaluated.
- Suggestions for updating existing documentation are planned, not implemented.

## Try it

The prepared demo needs no AI service. To generate answers from your own cases, SupportAI can use Google's Gemini AI, which sends case text to Google.

The app is available in English and Brazilian Portuguese. See the [setup guide](docs/developer-reference.md) to get started; installation needs some technical knowledge.
