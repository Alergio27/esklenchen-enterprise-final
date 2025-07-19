from flask import Blueprint, request, jsonify, session
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

auth_bp = Blueprint('auth', __name__)

# In-memory user storage (in production, use a proper database)
USERS = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'email': 'admin@esklenchen.com',
        'password_hash': generate_password_hash('esklenchen2025'),
        'role': 'admin',
        'full_name': 'Administrador ESKLENCHEN',
        'is_active': True,
        'created_at': datetime.utcnow(),
        'last_login': None,
        'failed_login_attempts': 0,
        'locked_until': None
    }
}

# JWT Secret key (in production, use environment variable)
JWT_SECRET = os.environ.get('JWT_SECRET', 'esklenchen-jwt-secret-key-2025')
JWT_EXPIRATION_HOURS = 24

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is missing'
            }), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = USERS.get(data['username'])
            
            if not current_user or not current_user['is_active']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or inactive user'
                }), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin privileges required'
            }), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/auth/login', methods=['POST'])
@cross_origin()
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        username = data['username'].lower()
        password = data['password']
        
        user = USERS.get(username)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Check if account is locked
        if user['locked_until'] and datetime.utcnow() < user['locked_until']:
            return jsonify({
                'success': False,
                'error': f'Account locked until {user["locked_until"].strftime("%Y-%m-%d %H:%M:%S")}'
            }), 423
        
        # Check if account is active
        if not user['is_active']:
            return jsonify({
                'success': False,
                'error': 'Account is deactivated'
            }), 401
        
        # Verify password
        if not check_password_hash(user['password_hash'], password):
            # Increment failed login attempts
            user['failed_login_attempts'] += 1
            
            # Lock account after 5 failed attempts
            if user['failed_login_attempts'] >= 5:
                user['locked_until'] = datetime.utcnow() + timedelta(minutes=30)
                return jsonify({
                    'success': False,
                    'error': 'Account locked due to multiple failed login attempts. Try again in 30 minutes.'
                }), 423
            
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Reset failed login attempts on successful login
        user['failed_login_attempts'] = 0
        user['locked_until'] = None
        user['last_login'] = datetime.utcnow()
        
        # Generate JWT token
        token_payload = {
            'username': username,
            'user_id': user['id'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'full_name': user['full_name'],
                'last_login': user['last_login'].isoformat() if user['last_login'] else None
            },
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # seconds
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@cross_origin()
@token_required
def logout(current_user):
    """User logout endpoint"""
    try:
        # In a real implementation, you might want to blacklist the token
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/me', methods=['GET'])
@cross_origin()
@token_required
def get_current_user(current_user):
    """Get current user information"""
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': current_user['id'],
                'username': current_user['username'],
                'email': current_user['email'],
                'role': current_user['role'],
                'full_name': current_user['full_name'],
                'last_login': current_user['last_login'].isoformat() if current_user['last_login'] else None,
                'created_at': current_user['created_at'].isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/change-password', methods=['POST'])
@cross_origin()
@token_required
def change_password(current_user):
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'error': 'Current password and new password are required'
            }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not check_password_hash(current_user['password_hash'], current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'error': 'New password must be at least 8 characters long'
            }), 400
        
        # Update password
        current_user['password_hash'] = generate_password_hash(new_password)
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/users', methods=['GET'])
@cross_origin()
@token_required
@admin_required
def get_users(current_user):
    """Get all users (admin only)"""
    try:
        users_list = []
        for username, user_data in USERS.items():
            users_list.append({
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data['role'],
                'full_name': user_data['full_name'],
                'is_active': user_data['is_active'],
                'created_at': user_data['created_at'].isoformat(),
                'last_login': user_data['last_login'].isoformat() if user_data['last_login'] else None,
                'failed_login_attempts': user_data['failed_login_attempts'],
                'locked_until': user_data['locked_until'].isoformat() if user_data['locked_until'] else None
            })
        
        return jsonify({
            'success': True,
            'users': users_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/users', methods=['POST'])
@cross_origin()
@token_required
@admin_required
def create_user(current_user):
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        username = data['username'].lower()
        
        # Check if username already exists
        if username in USERS:
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 400
        
        # Check if email already exists
        for user_data in USERS.values():
            if user_data['email'].lower() == data['email'].lower():
                return jsonify({
                    'success': False,
                    'error': 'Email already exists'
                }), 400
        
        # Validate password strength
        if len(data['password']) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        # Create new user
        new_user_id = max([user['id'] for user in USERS.values()]) + 1
        
        USERS[username] = {
            'id': new_user_id,
            'username': username,
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'role': data.get('role', 'user'),
            'full_name': data['full_name'],
            'is_active': True,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'failed_login_attempts': 0,
            'locked_until': None
        }
        
        return jsonify({
            'success': True,
            'user': {
                'id': new_user_id,
                'username': username,
                'email': data['email'],
                'role': data.get('role', 'user'),
                'full_name': data['full_name'],
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            },
            'message': 'User created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/users/<username>', methods=['PUT'])
@cross_origin()
@token_required
@admin_required
def update_user(current_user, username):
    """Update user (admin only)"""
    try:
        username = username.lower()
        
        if username not in USERS:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.get_json()
        user = USERS[username]
        
        # Update allowed fields
        updatable_fields = ['email', 'full_name', 'role', 'is_active']
        for field in updatable_fields:
            if field in data:
                user[field] = data[field]
        
        # Handle password update
        if 'password' in data:
            if len(data['password']) < 8:
                return jsonify({
                    'success': False,
                    'error': 'Password must be at least 8 characters long'
                }), 400
            user['password_hash'] = generate_password_hash(data['password'])
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'full_name': user['full_name'],
                'is_active': user['is_active']
            },
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/users/<username>', methods=['DELETE'])
@cross_origin()
@token_required
@admin_required
def delete_user(current_user, username):
    """Delete user (admin only)"""
    try:
        username = username.lower()
        
        if username not in USERS:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Prevent deleting the current admin user
        if username == current_user['username']:
            return jsonify({
                'success': False,
                'error': 'Cannot delete your own account'
            }), 400
        
        del USERS[username]
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/unlock-user/<username>', methods=['POST'])
@cross_origin()
@token_required
@admin_required
def unlock_user(current_user, username):
    """Unlock user account (admin only)"""
    try:
        username = username.lower()
        
        if username not in USERS:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user = USERS[username]
        user['failed_login_attempts'] = 0
        user['locked_until'] = None
        
        return jsonify({
            'success': True,
            'message': 'User account unlocked successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/reset-password-request', methods=['POST'])
@cross_origin()
def reset_password_request():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        email = data['email'].lower()
        
        # Find user by email
        user = None
        for user_data in USERS.values():
            if user_data['email'].lower() == email:
                user = user_data
                break
        
        # Always return success to prevent email enumeration
        if user:
            # Generate reset token (in production, store this securely)
            reset_token = secrets.token_urlsafe(32)
            user['reset_token'] = reset_token
            user['reset_token_expires'] = datetime.utcnow() + timedelta(hours=1)
            
            # In production, send email with reset link
            # send_password_reset_email(user['email'], reset_token)
        
        return jsonify({
            'success': True,
            'message': 'If the email exists, a password reset link has been sent'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/auth/verify-token', methods=['POST'])
@cross_origin()
def verify_token():
    """Verify JWT token validity"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is missing'
            }), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = USERS.get(data['username'])
        
        if not user or not user['is_active']:
            return jsonify({
                'success': False,
                'error': 'Invalid or inactive user'
            }), 401
        
        return jsonify({
            'success': True,
            'valid': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name']
            }
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            'success': False,
            'valid': False,
            'error': 'Token has expired'
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            'success': False,
            'valid': False,
            'error': 'Invalid token'
        }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

