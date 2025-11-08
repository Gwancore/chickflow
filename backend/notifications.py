from datetime import datetime
from models import db, Notification
from config import Config
import requests
from typing import Optional

class NotificationService:
    """Service for sending notifications via SMS, Email, and Push"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
    
    def send_order_confirmation(self, customer, order):
        """Send order confirmation notification"""
        message = (
            f"Hi {customer.farm_name}, your order {order.order_number} for {order.order_qty} "
            f"chicks has been received. Requested delivery: {order.requested_delivery_date}. "
            f"We'll notify you once allocated. - ChickFlow"
        )
        
        self._send_sms(customer.phone, message, 'customer', customer.id)
        
        if customer.email:
            subject = f"Order Confirmation - {order.order_number}"
            self._send_email(customer.email, subject, message, 'customer', customer.id)
    
    def send_allocation_notification(self, customer, allocation_data):
        """Send allocation confirmation"""
        message = (
            f"Great news {customer.farm_name}! {allocation_data['allocated_qty']} chicks "
            f"allocated for pickup today. Deadline: 2PM. Order: {allocation_data['order_number']}. "
            f"- ChickFlow"
        )
        
        self._send_sms(customer.phone, message, 'customer', customer.id)
        
        if customer.email:
            subject = "Chicks Allocated - Ready for Pickup"
            self._send_email(customer.email, subject, message, 'customer', customer.id)
        
        # Send push notification if available
        self._send_push_notification(
            customer.id, 
            "Chicks Allocated!", 
            message,
            'customer'
        )
    
    def send_waitlist_notification(self, customer, waitlist_data):
        """Send waitlist notification"""
        message = (
            f"Hi {customer.farm_name}, today's allocation is full. You're prioritized for "
            f"the next batch. Order: {waitlist_data.get('order_number', 'N/A')}. "
            f"Thank you for your patience! - ChickFlow"
        )
        
        self._send_sms(customer.phone, message, 'customer', customer.id)
        
        if customer.email:
            subject = "Order Waitlisted - Priority for Next Batch"
            self._send_email(customer.email, subject, message, 'customer', customer.id)
    
    def send_delivery_notification(self, customer, delivery):
        """Send delivery update notification"""
        message = (
            f"Hi {customer.farm_name}, your chicks are on the way! "
            f"Driver: {delivery.driver_name}, Vehicle: {delivery.vehicle_number}. "
            f"ETA: {delivery.estimated_arrival.strftime('%I:%M %p') if delivery.estimated_arrival else 'TBD'}. "
            f"- ChickFlow"
        )
        
        self._send_sms(customer.phone, message, 'customer', customer.id)
        self._send_push_notification(customer.id, "Delivery in Progress", message, 'customer')
    
    def _send_sms(self, phone: str, message: str, recipient_type: str, recipient_id: int) -> bool:
        """Send SMS via Twilio"""
        notification = Notification(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            recipient_contact=phone,
            notification_type='sms',
            message=message,
            status='pending'
        )
        
        try:
            if not self.config.TWILIO_ACCOUNT_SID or not self.config.TWILIO_AUTH_TOKEN:
                print(f"SMS (simulated): {phone} - {message}")
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            else:
                from twilio.rest import Client
                client = Client(self.config.TWILIO_ACCOUNT_SID, self.config.TWILIO_AUTH_TOKEN)
                
                msg = client.messages.create(
                    body=message,
                    from_=self.config.TWILIO_PHONE_NUMBER,
                    to=phone
                )
                
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            
            db.session.add(notification)
            db.session.commit()
            return True
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            db.session.add(notification)
            db.session.commit()
            print(f"SMS Error: {e}")
            return False
    
    def _send_email(self, email: str, subject: str, message: str, 
                   recipient_type: str, recipient_id: int) -> bool:
        """Send email via SendGrid"""
        notification = Notification(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            recipient_contact=email,
            notification_type='email',
            subject=subject,
            message=message,
            status='pending'
        )
        
        try:
            if not self.config.SENDGRID_API_KEY:
                print(f"Email (simulated): {email} - {subject}")
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            else:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                
                mail = Mail(
                    from_email=self.config.FROM_EMAIL,
                    to_emails=email,
                    subject=subject,
                    html_content=f"<p>{message}</p>"
                )
                
                sg = SendGridAPIClient(self.config.SENDGRID_API_KEY)
                response = sg.send(mail)
                
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            
            db.session.add(notification)
            db.session.commit()
            return True
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            db.session.add(notification)
            db.session.commit()
            print(f"Email Error: {e}")
            return False
    
    def _send_push_notification(self, user_id: int, title: str, message: str, 
                               recipient_type: str) -> bool:
        """Send push notification via Firebase Cloud Messaging"""
        notification = Notification(
            recipient_type=recipient_type,
            recipient_id=user_id,
            recipient_contact=f"user_{user_id}",
            notification_type='push',
            subject=title,
            message=message,
            status='pending'
        )
        
        try:
            if not self.config.FCM_SERVER_KEY:
                print(f"Push (simulated): {title} - {message}")
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            else:
                # FCM implementation
                # This would require device tokens stored in user/customer profile
                headers = {
                    'Authorization': f'key={self.config.FCM_SERVER_KEY}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'notification': {
                        'title': title,
                        'body': message
                    },
                    'to': f'/topics/user_{user_id}'  # Or use device token
                }
                
                response = requests.post(
                    'https://fcm.googleapis.com/fcm/send',
                    headers=headers,
                    json=payload
                )
                
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            
            db.session.add(notification)
            db.session.commit()
            return True
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            db.session.add(notification)
            db.session.commit()
            print(f"Push Notification Error: {e}")
            return False
