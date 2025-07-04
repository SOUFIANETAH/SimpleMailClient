# SimpleMailClient

A simple command-line email client written in Python using `openssl s_client` to send and receive emails via **SMTP**, **POP3**, and **IMAP** protocols.  
Built for testing, learning, and understanding how email protocols work at a low level — **not for production use**.

---

## ⚠️ Disclaimer

> This tool is for educational/testing purposes only.  
> **Do not use real or sensitive email credentials**.  
> Passwords are entered in plain text for simplicity and transparency during testing.

---

## 📦 Requirements

- Python 3.6+
- OpenSSL installed on your system (`openssl s_client` must be available in terminal)

You can verify OpenSSL is available by running:

```bash
openssl version
