# Privacy Policy

Last updated: 2026-06-15

## Overview

discord-notifier is a private, self-hosted Discord notification tool for creator live streams and community updates.

The application uses the YouTube Data API to read public channel and live stream metadata, and sends notification messages to a configured Discord channel via Discord webhook.

## Data Collected

This project does not collect personal data from users.

The application does not collect, store, or process:

* YouTube user accounts
* OAuth tokens
* Google account information
* Discord user accounts
* Personal information
* Payment information
* Private YouTube data

## YouTube Data Usage

This project only reads public YouTube metadata required for live stream notifications, such as:

* Public channel metadata
* Public live stream metadata
* Public video title and URL
* Public thumbnail URL

The application does not upload, modify, delete, or manage YouTube content.

## Local State

The application may store minimal local state on the self-hosted server, such as previously notified video IDs, only to prevent duplicate Discord notifications.

This local state is not shared with third parties.

## Discord Webhook Usage

When a live stream or supported update is detected, the application sends a notification message to the configured Discord webhook URL.

The Discord webhook URL is provided by the operator and is not shared publicly by the application.

## Third Parties

This project uses:

* YouTube Data API, to read public YouTube metadata
* Discord Webhooks, to send notification messages to Discord

No personal data is sold, shared, or transferred to third parties.

## Contact

For questions about this project or its privacy practices, please contact the repository owner through GitHub.
