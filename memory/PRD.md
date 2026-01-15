# COME Email Campaign Manager - PRD

## Original Problem Statement
Professional email campaign manager like Dream11 for COME app. Features include:
- Login with credentials (aryan/726339)
- Create email campaigns with Dream11 style (dark theme, winning amount, team logos, breakup table, green CTA)
- Manage cricket team & tournament logos
- Send professional HTML emails via Resend API

## Architecture
- **Backend**: FastAPI with MongoDB
- **Frontend**: React with Tailwind CSS
- **Email Service**: Resend API
- **Auth**: JWT-based authentication

## User Personas
1. **Campaign Manager**: Creates and sends winning email campaigns
2. **Admin**: Manages team/tournament logos

## Core Requirements
- [x] Login/Authentication system
- [x] Dashboard with stats
- [x] Email campaign creation with form
- [x] Dream11-style email template
- [x] Team logo management (10 teams)
- [x] Tournament logo management (3 tournaments)
- [x] Email preview before sending
- [x] Campaign history

## What's Been Implemented (Jan 15, 2025)
1. **Login Page**: Dark theme with COME rainbow logo
2. **Dashboard**: Stats cards, quick actions, recent campaigns
3. **Create Campaign**: Split view with form + live preview
4. **Logo Manager**: Tabs for teams/tournaments, add/delete logos
5. **Campaign History**: List with preview/send/delete actions
6. **Email Template**: Dream11 style with dark bg, green CTA, winning breakup

## API Endpoints
- POST /api/auth/login - User login
- GET /api/stats - Dashboard statistics
- POST /api/campaigns - Create campaign
- GET /api/campaigns - List campaigns
- POST /api/campaigns/{id}/preview - Get email HTML
- POST /api/campaigns/{id}/send - Send email
- GET/POST/DELETE /api/logos - Logo management
- POST /api/seed-logos - Seed default logos

## Credentials
- Username: aryan, Password: 726339
- Resend API Key: Configured in backend

## Prioritized Backlog
### P0 (Completed)
- [x] Core email sending functionality
- [x] Dream11-style template

### P1 (Future)
- [ ] Custom domain email sending
- [ ] Bulk email campaigns
- [ ] Email scheduling

### P2 (Nice to Have)
- [ ] Email analytics (open rates, clicks)
- [ ] Template customization
- [ ] Export campaign reports

## Next Tasks
1. Add IPL team logos (CSK, MI, RCB, etc.)
2. Custom email domain setup for production
3. Email analytics dashboard
