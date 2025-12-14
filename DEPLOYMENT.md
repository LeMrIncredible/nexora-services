# Deployment Guide

This guide explains how to deploy the Nexora project into a production environment.  Although the project runs out‑of‑the‑box with Node.js and no external dependencies, production deployment requires proper environment configuration, secure secrets management and an understanding of how to serve the application over HTTPS.

## 1. Prepare the Environment

1. **Clone the repository** to your server:
   ```bash
   git clone <your-fork-url> nexora
   cd nexora
   ```
2. **Install Node.js** if it’s not already installed.  Version 14 or higher is recommended.
3. **Create a `.env` file** by copying `.env.example` and filling in your values:
   ```bash
   cp .env.example .env
   # edit .env with your credentials and settings
   ```
   Do not commit `.env` to version control.  Ensure that file permissions restrict access to authorised users only.

## 2. Start the Server

To run the server directly (not recommended for long‑running production use):

```bash
node server.js
```

This will start the HTTP server on the port defined in `.env` (default `3000`).  You can visit `http://your-domain.com:3000/` to confirm it’s running.

### Using a Process Manager

For reliability you should run the Node process under a process manager such as [`pm2`](https://pm2.keymetrics.io/) or [`systemd`].  Example with pm2:

```bash
npm install -g pm2
pm2 start server.js --name nexora
pm2 save
pm2 startup
```

This will ensure the application starts on boot and restarts if it crashes.

## 3. Configure a Reverse Proxy

In production it is common to place your Node.js application behind a web server like **Nginx** or **Apache** which handles SSL termination, compression and routing.  Here is a minimal Nginx configuration snippet:

```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Replace `your-domain.com` and adjust the proxy port to match your `.env` `PORT` value.  Don’t forget to configure HTTPS using Let’s Encrypt or another certificate authority.

## 4. Google Workspace Credentials

If you intend to integrate the automations with Google Sheets, Gmail or Calendar, copy your service account JSON file to the server and update `GOOGLE_SERVICE_ACCOUNT_KEYFILE` in `.env` with the absolute path.  See `GOOGLE_WORKSPACE_SETUP.md` for instructions on creating and sharing the service account.

## 5. Updating the Application

When you make changes to the code:
1. Pull the latest changes on the server.
2. Restart the Node process.  With pm2 you can run `pm2 restart nexora`.

## 6. Troubleshooting

* **Server does not start** – Ensure your `.env` file is valid.  The server will not load credentials from anywhere else.
* **Port already in use** – Change `PORT` in `.env` or stop the process currently using that port.
* **Logs not written** – The `logs/` directory is created at runtime.  Ensure the Node process has write permissions in the project directory.
* **Audit submissions not saved** – Confirm the `data/` directory exists and that the user running the Node process can write to it.

## 7. Next Steps

This deployment guide covers only the basics.  For production you may wish to:

* Set up HTTPS with automatic certificate renewal.
* Configure a firewall to limit access to the Node process.
* Use a real database instead of CSV files for storing leads and audit submissions.
* Integrate a monitoring solution to alert you on errors.

By following this guide you can take the Nexora platform from development to production with confidence.  If you encounter issues not covered here, consult your hosting provider’s documentation or seek professional assistance.
