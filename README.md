# Summoner

A lightweight app wrapper around the Bamboo HR direcotry for sending notifications via SMS, Email or Slack.

Runs on appengine, uses twilio for SMS and Slack's Incoming Webhooks API for messaging.

# Configuration
Copy `app.template.yaml` and fill in the appropriate keys (or find your organization's existing config)

`app.yaml` is gitignored to avoid committing keys.

## Slack
Generate an "Incoming Webhook" integration key. You can pick any channel when you create the hook – the value is ignored.

## Twilio
You need to compute the base64 encoded auth hash as described in Twilio docs.

## BambooHR

The key used needs to have access to:

- id
- displayName
- workEmail
- department
- status
- jobTitle
- mobilePhone
- homePhone (optional, used as fallback)
- workPhone (optional, used as fallback)


