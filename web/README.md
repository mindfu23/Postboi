# Postboi Web Starter

This directory contains starter templates and configuration for the Postboi web application.

## 🚀 Quick Start

1. **Copy the environment template:**
   ```bash
   cp ../.env.template ../.env
   ```

2. **Configure your credentials** in the `.env` file

3. **Open `index.html`** in your browser to see the starter template

## 🛠️ Setup for Production

For a production web application, you'll need:

### Backend Setup (Node.js Example)

1. **Install dependencies:**
   ```bash
   npm init -y
   npm install express dotenv multer axios
   ```

2. **Create a backend server:**
   ```javascript
   // server.js
   require('dotenv').config();
   const express = require('express');
   const app = express();
   
   app.use(express.json());
   app.use(express.static('public'));
   
   // API endpoint to handle posting
   app.post('/api/post', async (req, res) => {
       // Use environment variables for API calls
       const config = {
           facebook: {
               pageId: process.env.FACEBOOK_PAGE_ID,
               accessToken: process.env.FACEBOOK_ACCESS_TOKEN
           }
       };
       
       // Handle API calls securely on the backend
       // ... your posting logic here
   });
   
   const PORT = process.env.PORT || 3000;
   app.listen(PORT, () => {
       console.log(`Server running on port ${PORT}`);
   });
   ```

3. **Run the server:**
   ```bash
   node server.js
   ```

### Frontend Frameworks

This starter template uses vanilla HTML/CSS/JavaScript. For production apps, consider:

- **React**: `npx create-react-app postboi-web`
- **Vue**: `npm init vue@latest`
- **Angular**: `ng new postboi-web`

## 🔐 Security Best Practices

1. **Never expose API keys in client-side code**
2. **Use environment variables** for all sensitive data
3. **Implement authentication** for your web app
4. **Use HTTPS** in production
5. **Validate and sanitize** all user inputs
6. **Implement rate limiting** to prevent abuse

## 📚 API Integration

The web app should call your backend API, which then makes requests to:

- **WordPress REST API**: For blog posting
- **Facebook Graph API**: For Facebook page posting
- **Instagram Graph API**: For Instagram business account posting

See the main [README.md](../README.md) for detailed API setup instructions.

## 🔗 Related Files

- `../.env.template` - Environment variable template
- `../config.py` - Python configuration (for reference)
- `../README.md` - Main project documentation
