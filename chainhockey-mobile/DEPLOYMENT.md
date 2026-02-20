# 🚀 Chain Hockey Mobile - Deployment Guide

## Quick Start (Fastest Method)

### Run Locally
```bash
cd /app/chainhockey-mobile
python3 -m http.server 8080
```
Open browser: **http://localhost:8080**

---

## 📱 Mobile Testing

### On Same Network
1. Start server on your computer
2. Find your IP address:
   - **Mac/Linux**: `ifconfig | grep inet`
   - **Windows**: `ipconfig`
3. On mobile: `http://YOUR_IP:8080`

### Example:
If your IP is `192.168.1.100`:
- Mobile browser: `http://192.168.1.100:8080`

---

## 🌐 Deploy to Web

### Option 1: GitHub Pages (Free)
```bash
# In chainhockey-mobile directory
git init
git add .
git commit -m "Chain Hockey Mobile"
git branch -M main
git remote add origin YOUR_REPO_URL
git push -u origin main

# Enable GitHub Pages in repo settings
# Source: main branch, root folder
```

Your game will be live at: `https://YOUR_USERNAME.github.io/REPO_NAME`

### Option 2: Netlify (Free, Easiest)
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop the `chainhockey-mobile` folder
3. Done! Get instant URL

### Option 3: Vercel (Free)
```bash
npm install -g vercel
cd chainhockey-mobile
vercel
```

### Option 4: Firebase Hosting (Free)
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Select chainhockey-mobile as public directory
firebase deploy
```

---

## 📦 Package as Mobile App

### Using Capacitor (Recommended)

#### Setup:
```bash
npm install @capacitor/core @capacitor/cli
npx cap init ChainHockey com.yourdomain.chainhockey --web-dir .
```

#### Add Platforms:
```bash
# iOS
npx cap add ios
npx cap open ios

# Android
npx cap add android
npx cap open android
```

#### Configure `capacitor.config.json`:
```json
{
  "appId": "com.yourdomain.chainhockey",
  "appName": "Chain Hockey",
  "webDir": ".",
  "bundledWebRuntime": false
}
```

### Using Cordova

```bash
cordova create ChainHockeyApp com.yourdomain.chainhockey ChainHockey
cd ChainHockeyApp
# Copy all files to www/
cordova platform add android
cordova platform add ios
cordova build android
```

---

## 🔧 Advanced Deployment

### Using Docker
Create `Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t chainhockey .
docker run -p 8080:80 chainhockey
```

### Using Cloud Platforms

#### AWS S3 + CloudFront
```bash
aws s3 sync . s3://your-bucket --acl public-read
# Set up CloudFront distribution
```

#### Google Cloud Storage
```bash
gsutil -m cp -r * gs://your-bucket
gsutil iam ch allUsers:objectViewer gs://your-bucket
```

#### Azure Static Web Apps
```bash
az staticwebapp create --name ChainHockey --source .
```

---

## 🎮 PWA (Progressive Web App)

Add `manifest.json`:
```json
{
  "name": "Chain Hockey",
  "short_name": "ChainHockey",
  "start_url": "/",
  "display": "fullscreen",
  "orientation": "landscape",
  "background_color": "#000000",
  "theme_color": "#000000",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Add to `index.html` `<head>`:
```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#000000">
```

---

## 🔍 Testing Checklist

- [ ] Game loads without errors
- [ ] Touch controls work on both sides
- [ ] Puck physics working
- [ ] Chains render and move correctly
- [ ] Score updates when goals are scored
- [ ] Timer counts down
- [ ] Pause menu works
- [ ] Game over screen appears
- [ ] Restart works
- [ ] Works in landscape orientation
- [ ] Works on different screen sizes

---

## 📊 Performance Tips

1. **Enable Physics Debug** (if needed):
   ```javascript
   // In game/config.js
   matter: {
       debug: true  // Shows collision bodies
   }
   ```

2. **Optimize for Low-End Devices**:
   ```javascript
   // Reduce chain segments
   CHAIN: { SEGMENTS: 5 }
   
   // Lower FPS
   fps: { target: 30 }
   ```

3. **Monitor Performance**:
   ```javascript
   // In GameScene create()
   this.time.addEvent({
       delay: 1000,
       callback: () => {
           console.log('FPS:', this.game.loop.actualFps);
       },
       loop: true
   });
   ```

---

## 🐛 Troubleshooting

### Game doesn't load
- Check console for errors (F12)
- Ensure served via HTTP (not file://)
- Check Phaser CDN is accessible

### Touch not working
- Verify touch-action CSS is applied
- Check browser console for errors
- Test with mouse first (should work same way)

### Physics feels weird
- Adjust mass values in `game/config.js`
- Tune chain stiffness/damping
- Modify friction/restitution

### Low FPS on mobile
- Reduce chain segments
- Lower particle count
- Disable debug mode
- Simplify graphics

---

## 📝 Customization

All settings in `game/config.js`:
- Game duration
- Goal limit
- Physics parameters
- Colors
- Sizes
- Chain properties

---

## 🎯 Next Steps

1. **Add Sound Effects**
   - Collision sounds
   - Goal sounds
   - Background music

2. **Add Power-ups**
   - Speed boost
   - Bigger hammer
   - Freeze opponent

3. **Network Multiplayer**
   - WebSocket server
   - Room system
   - Sync game state

4. **Analytics**
   - Google Analytics
   - Track plays, goals, avg game time

5. **Leaderboards**
   - Firebase Realtime Database
   - Track high scores

---

## 📄 License

MIT License - Free to use, modify, and distribute!

---

**Enjoy your Chain Hockey game! 🏒🎮**
