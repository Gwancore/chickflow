# Deployment Guide

## Prerequisites

- Server with Ubuntu 20.04+ or similar Linux distribution
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database
- Redis server
- Node.js 16+
- Python 3.8+

## Backend Deployment

### Option 1: Deploy to Heroku

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create Heroku app**
```bash
cd backend
heroku login
heroku create chickflow-api
```

3. **Add PostgreSQL addon**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. **Add Redis addon**
```bash
heroku addons:create heroku-redis:hobby-dev
```

5. **Set environment variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret
heroku config:set FLASK_ENV=production
heroku config:set TWILIO_ACCOUNT_SID=your-twilio-sid
heroku config:set TWILIO_AUTH_TOKEN=your-twilio-token
heroku config:set SENDGRID_API_KEY=your-sendgrid-key
```

6. **Create Procfile**
```bash
echo "web: gunicorn app:app" > Procfile
```

7. **Deploy**
```bash
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a chickflow-api
git push heroku main
```

8. **Run migrations**
```bash
heroku run flask db upgrade
```

### Option 2: Deploy to DigitalOcean/AWS

1. **Create a droplet/EC2 instance** (Ubuntu 20.04)

2. **SSH into server**
```bash
ssh root@your-server-ip
```

3. **Update system**
```bash
apt update && apt upgrade -y
```

4. **Install dependencies**
```bash
apt install python3-pip python3-venv postgresql postgresql-contrib redis-server nginx -y
```

5. **Create app user**
```bash
adduser chickflow
usermod -aG sudo chickflow
su - chickflow
```

6. **Clone repository**
```bash
git clone https://github.com/yourusername/chickflow.git
cd chickflow/backend
```

7. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

8. **Create .env file**
```bash
nano .env
# Add your environment variables
```

9. **Setup PostgreSQL**
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE chickflow;
CREATE USER chickflow WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE chickflow TO chickflow;
\q
```

10. **Update DATABASE_URL in .env**
```
DATABASE_URL=postgresql://chickflow:your-password@localhost/chickflow
```

11. **Run migrations**
```bash
flask db upgrade
```

12. **Create systemd service**
```bash
sudo nano /etc/systemd/system/chickflow.service
```

Add:
```ini
[Unit]
Description=ChickFlow API
After=network.target

[Service]
User=chickflow
WorkingDirectory=/home/chickflow/chickflow/backend
Environment="PATH=/home/chickflow/chickflow/backend/venv/bin"
ExecStart=/home/chickflow/chickflow/backend/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

13. **Start service**
```bash
sudo systemctl start chickflow
sudo systemctl enable chickflow
sudo systemctl status chickflow
```

14. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/chickflow
```

Add:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

15. **Enable site**
```bash
sudo ln -s /etc/nginx/sites-available/chickflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

16. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

## Frontend Deployment

### Option 1: Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
cd frontend
vercel
```

3. **Set environment variables in Vercel dashboard**
- Go to project settings
- Add environment variables
- Set API base URL

### Option 2: Deploy to Netlify

1. **Build the app**
```bash
cd frontend
npm run build
```

2. **Install Netlify CLI**
```bash
npm i -g netlify-cli
```

3. **Deploy**
```bash
netlify deploy --prod --dir=dist
```

### Option 3: Self-host with Nginx

1. **Build the app**
```bash
cd frontend
npm run build
```

2. **Copy to server**
```bash
scp -r dist/* chickflow@your-server:/var/www/chickflow
```

3. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/chickflow-web
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/chickflow;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Enable and restart**
```bash
sudo ln -s /etc/nginx/sites-available/chickflow-web /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

5. **Setup SSL**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Mobile App Deployment

### Build for Android

1. **Configure app.json**
```json
{
  "expo": {
    "android": {
      "package": "com.chickflow.mobile",
      "versionCode": 1
    }
  }
}
```

2. **Build APK**
```bash
cd mobile
expo build:android
```

3. **Download and distribute APK**

### Build for iOS

1. **Configure app.json**
```json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.chickflow.mobile",
      "buildNumber": "1.0.0"
    }
  }
}
```

2. **Build IPA**
```bash
expo build:ios
```

3. **Submit to App Store**

### Publish to Expo

```bash
expo publish
```

## Database Backups

### Automated backups

1. **Create backup script**
```bash
nano /home/chickflow/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/chickflow/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump chickflow > $BACKUP_DIR/chickflow_$DATE.sql
find $BACKUP_DIR -name "chickflow_*.sql" -mtime +7 -delete
```

2. **Make executable**
```bash
chmod +x /home/chickflow/backup.sh
```

3. **Add to crontab**
```bash
crontab -e
```

Add:
```
0 2 * * * /home/chickflow/backup.sh
```

## Monitoring

### Setup PM2 (Alternative to systemd)

```bash
npm install -g pm2
cd backend
pm2 start "gunicorn app:app -b 0.0.0.0:5000" --name chickflow-api
pm2 startup
pm2 save
```

### Logs

```bash
# Systemd logs
sudo journalctl -u chickflow -f

# PM2 logs
pm2 logs chickflow-api

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Environment Variables Reference

### Backend (.env)
```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

DATABASE_URL=postgresql://user:password@localhost:5432/chickflow
REDIS_URL=redis://localhost:6379/0

TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@chickflow.com

FCM_SERVER_KEY=your-fcm-key

MAX_PER_CUSTOMER=1000
WAITING_PERIOD_DAYS=7
PICKUP_DEADLINE_HOUR=14
```

### Frontend (.env)
```env
VITE_API_URL=https://api.yourdomain.com
```

### Mobile (app.json)
```json
{
  "extra": {
    "apiUrl": "https://api.yourdomain.com"
  }
}
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Setup SSL/TLS certificates
- [ ] Configure firewall (UFW)
- [ ] Disable root SSH login
- [ ] Setup fail2ban
- [ ] Enable database encryption
- [ ] Regular security updates
- [ ] Setup CORS properly
- [ ] Implement rate limiting
- [ ] Regular backups
- [ ] Monitor logs

## Performance Optimization

1. **Enable gzip compression in Nginx**
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

2. **Setup Redis caching**

3. **Database indexing**
```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_allocations_date ON allocations(allocation_date);
```

4. **CDN for static assets**

## Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u chickflow -n 50

# Check if port is in use
sudo lsof -i :5000

# Test manually
source venv/bin/activate
python app.py
```

### Database connection issues
```bash
# Test PostgreSQL connection
psql -U chickflow -d chickflow

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Nginx errors
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

## Support

For deployment issues:
- Email: support@chickflow.com
- Documentation: https://docs.chickflow.com
- GitHub Issues: https://github.com/yourusername/chickflow/issues
