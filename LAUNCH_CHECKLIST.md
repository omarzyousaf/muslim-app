# Pre-Launch Checklist
## Before Making App Public

### Cost & Rate Controls
- [ ] Add rate limiting to Islamic Scholar chat (max 20 messages per session per device)
- [ ] Add `max_tokens` limit of 500 per response on the AI chat to control costs
- [ ] Add access code or password so only invited users can access the AI chat feature
- [ ] Set a monthly spending limit on Anthropic console (console.anthropic.com)
- [ ] Set a monthly spending limit on Supabase

### Access & Security
- [ ] Add Streamlit authentication if opening to general public
- [ ] Make sure `.env` secrets are all added to Streamlit Cloud secrets
- [ ] Verify Supabase project is not paused

### Testing
- [ ] Test app on mobile (iPhone home screen)
- [ ] Test all 4 tabs work correctly on live URL
- [ ] Test GPS location detection on mobile
- [ ] Test prayer tracker saves correctly across sessions
