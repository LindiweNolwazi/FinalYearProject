// ===== REGISTRATION & LOGIN =====
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async e => {
        e.preventDefault();
        const role = document.getElementById('regRole').value;
        const full_name = document.getElementById('regFullName').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        
        if (password !== confirmPassword) { 
            alert("Passwords do not match!"); 
            return; 
        }
        
        let organization = role === 'sponsor' ? document.getElementById('regOrganization').value : "";
        let cellphone_number = role === 'student' ? document.getElementById('regStudentNumber').value : "";

        try {
            const res = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role, full_name, email, password, cellphone_number, organization })
            });
            
            const data = await res.json();
            
            if (res.ok) {
                alert(`${role} registered successfully!`);
                window.location.href = role === 'student' ? '/student-login' : '/sponsor-login';
            } else {
                alert(data.error || "Registration failed");
            }
        } catch(err) { 
            console.error("Registration error:", err); 
            alert("Server error - please try again later"); 
        }
    });
}

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async e => {
        e.preventDefault();
        const role = document.getElementById('loginRole').value;
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const res = await fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role, email, password })
            });
            
            // Check if response is OK before parsing JSON
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            
            const data = await res.json();
            
            if (data.access_token) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('role', data.role || role);
                localStorage.setItem('user', JSON.stringify(data.user || {}));

                if (role === 'student') {
                    window.location.href = '/student-dashboard';
                } else if (role === 'sponsor') {
                    window.location.href = '/sponsor-dashboard';
                } else if (role === 'admin') {
                    window.location.href = '/admin-dashboard';
                }
            } else {
                alert(data.error || "Login failed - no token received");
            }
        } catch(err) { 
            console.error("Login error:", err); 
            alert("Login failed - please check your credentials and try again"); 
        }
    });
}

// ===== API HELPER FUNCTIONS =====
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`http://127.0.0.1:5000${url}`, mergedOptions);
        
        // Check if unauthorized (token expired)
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/';
            throw new Error('Session expired. Please login again.');
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// ===== STUDENT DASHBOARD =====
(async function() {
    // Check if we're on the student dashboard page
    if (window.location.pathname === '/student-dashboard' || document.querySelector('#studentApplicationsTable')) {
        const token = localStorage.getItem('token');
        const role = localStorage.getItem('role');

        // Redirect if not student or no token
        if (!token || role !== 'student') {
            window.location.href = '/student-login';
            return;
        }

        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.clear();
            window.location.href = '/student-login';
        });

        // Load student applications
        try {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const applications = await apiRequest(`/student/applications?student_id=${user.student_id || ''}`);
            const tbody = document.getElementById('studentApplicationsTable').querySelector('tbody');

            applications.forEach(app => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${app.application_type || 'N/A'}</td>
                    <td>${app.title || 'N/A'}</td>
                    <td>${app.status || 'pending'}</td>
                `;
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Failed to load applications:', error);
        }

        // Load student notifications
        try {
            const notifications = await apiRequest('/student/notifications');
            const notificationsList = document.getElementById('notificationsList');

            if (notifications.length === 0) {
                notificationsList.innerHTML = '<p>No notifications yet.</p>';
            } else {
                notifications.forEach(notification => {
                    const notificationDiv = document.createElement('div');
                    notificationDiv.className = `notification ${notification.is_read ? '' : 'unread'}`;
                    notificationDiv.innerHTML = `
                        <div class="message">${notification.message}</div>
                        <div class="date">${new Date(notification.created_at).toLocaleString()}</div>
                        ${!notification.is_read ? `<button class="mark-read" data-id="${notification.notification_id}">Mark as Read</button>` : ''}
                    `;
                    notificationsList.appendChild(notificationDiv);
                });

                // Add event listeners for mark as read buttons
                document.querySelectorAll('.mark-read').forEach(btn => {
                    btn.addEventListener('click', async () => {
                        const notificationId = btn.getAttribute('data-id');
                        try {
                            await apiRequest('/student/notifications/mark-read', {
                                method: 'POST',
                                body: JSON.stringify({ notification_id: notificationId })
                            });
                            btn.parentElement.classList.remove('unread');
                            btn.remove();
                        } catch (error) {
                            console.error('Failed to mark notification as read:', error);
                            alert('Failed to mark notification as read.');
                        }
                    });
                });
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }
})();

// ===== SPONSOR DASHBOARD =====
(async function() {
    if (document.getElementById('sponsorFundForm')) {
        const token = localStorage.getItem('token');
        const role = localStorage.getItem('role');
        
        // Redirect if not sponsor or no token
        if (!token || role !== 'sponsor') {
            window.location.href = '/sponsor-login';
            return;
        }

        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.clear();
            window.location.href = '/sponsor-login';
        });

        // Load funding opportunities
        try {
            const opportunities = await apiRequest('/funding/list');
            const oppSelect = document.getElementById('fundOpportunityId');
            
            opportunities.forEach(opp => {
                const option = document.createElement('option');
                option.value = opp.opportunity_id;
                option.textContent = `${opp.title} (${opp.funding_type}) - R ${opp.funding_amount}`;
                oppSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load funding opportunities:', error);
            alert('Failed to load funding opportunities. Please try again later.');
        }

        // Load sponsor transactions
        try {
            const transactions = await apiRequest('/sponsor/transactions');
            const tbody = document.getElementById('sponsorTransactionsTable').querySelector('tbody');
            
            transactions.forEach(transaction => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${transaction.student_name || 'N/A'}</td>
                    <td>${transaction.title || 'N/A'}</td>
                    <td>R ${transaction.amount || '0'}</td>
                    <td>${transaction.payment_method || 'N/A'}</td>
                    <td>${transaction.status || 'pending'}</td>
                `;
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Failed to load transactions:', error);
        }

    // Handle funding submission
    document.getElementById('sponsorFundForm').addEventListener('submit', async e => {
      e.preventDefault();
      const student_id = document.getElementById('fundStudentId').value;
      const opportunity_id = document.getElementById('fundOpportunityId').value;
      const amount = document.getElementById('fundAmount').value;

      try {
        const result = await apiRequest('/sponsor/fund', {
          method: 'POST',
          body: JSON.stringify({ student_id, opportunity_id, amount })
        });

        alert(result.message || 'Funding request submitted successfully!');
        if (result.transaction_id) {
          // Redirect directly to payment page - the authentication should work now
          window.location.href = `/payment/${result.transaction_id}`;
        } else {
          window.location.reload();
        }
      } catch (error) {
        console.error('Funding failed:', error);
        alert('Failed to process funding. Please try again.');
      }
    });
    }
})();

// ===== GENERAL UTILITY FUNCTIONS =====
// Check authentication status on page load
function checkAuth() {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop();

    // Pages that require authentication
    const protectedPages = ['student-dashboard', 'sponsor-dashboard', 'admin-dashboard'];
    const isPaymentPage = currentPath.startsWith('/payment/');

    if ((protectedPages.includes(currentPage) || isPaymentPage) && !token) {
        window.location.href = '/';
        return;
    }

    // Role-specific redirects
    if (currentPage === 'student-dashboard' && role !== 'student') {
        window.location.href = '/student-login';
    }

    if (currentPage === 'sponsor-dashboard' && role !== 'sponsor') {
        window.location.href = '/sponsor-login';
    }

    if (currentPage === 'admin-dashboard' && role !== 'admin') {
        window.location.href = '/admin-login';
    }

    // Payment pages should only be accessible by sponsors
    if (isPaymentPage && role !== 'sponsor') {
        window.location.href = '/sponsor-login';
    }
}

// Run authentication check when page loads
document.addEventListener('DOMContentLoaded', checkAuth);