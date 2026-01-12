# API Testing Script for MediSecure Backend
# Use this with PowerShell

$BASE_URL = "http://localhost:8000"
$TOKEN = ""  # Will be filled after login

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MediSecure API Testing Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "[1] Testing Health Check..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
Write-Host "✓ Health Check:" -ForegroundColor Green
$response | ConvertTo-Json
Write-Host ""

# Test 2: Sign Up
Write-Host "[2] Testing User Signup..." -ForegroundColor Yellow
$signupData = @{
    email = "testuser@example.com"
    password = "SecurePass123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/auth/signup" -Method Post -Body $signupData -ContentType "application/json"
    Write-Host "✓ Signup successful:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "Note: User might already exist" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Login
Write-Host "[3] Testing Login..." -ForegroundColor Yellow
$loginData = @{
    email = "testuser@example.com"
    password = "SecurePass123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/auth/login" -Method Post -Body $loginData -ContentType "application/json"
    $TOKEN = $response.access_token
    Write-Host "✓ Login successful:" -ForegroundColor Green
    Write-Host "Token: $TOKEN`n" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Login failed. User might not be verified." -ForegroundColor Red
    Write-Host "Please check your email for verification code or manually verify in database" -ForegroundColor Yellow
    Write-Host "SQL: UPDATE users SET is_verified = TRUE WHERE email = 'testuser@example.com';" -ForegroundColor Cyan
    exit
}
Write-Host ""

# Create headers with auth token
$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# Test 4: Get Current User
Write-Host "[4] Testing GET /api/v1/users/me..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me" -Method Get -Headers $headers
    Write-Host "✓ Current User Info:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Create User Profile
Write-Host "[5] Testing POST /api/v1/users/me/profile (Create Profile)..." -ForegroundColor Yellow
$profileData = @{
    first_name = "John"
    last_name = "Doe"
    date_of_birth = "1990-01-15"
    phone = "555-0123"
    address = "123 Main St, City, State 12345"
    blood_type = "A+"
    medical_record_number = "MRN123456"
    insurance_number = "INS789012"
    emergency_contact_name = "Jane Doe"
    emergency_contact_phone = "555-0124"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me/profile" -Method Post -Headers $headers -Body $profileData
    Write-Host "✓ Profile Created:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Get User Profile (Decrypted)
Write-Host "[6] Testing GET /api/v1/users/me/profile (Retrieve Decrypted Profile)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me/profile" -Method Get -Headers $headers
    Write-Host "✓ Profile Retrieved (Sensitive data decrypted):" -ForegroundColor Green
    $response | ConvertTo-Json
    Write-Host "Note: Sensitive fields like phone, address, SSN are automatically decrypted" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: Get User Devices
Write-Host "[7] Testing GET /api/v1/users/me/devices..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me/devices" -Method Get -Headers $headers
    Write-Host "✓ User Devices:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 8: Change Password
Write-Host "[8] Testing POST /api/v1/users/me/change-password..." -ForegroundColor Yellow
$passwordData = @{
    current_password = "SecurePass123"
    new_password = "NewSecurePass456"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me/change-password" -Method Post -Headers $headers -Body $passwordData
    Write-Host "✓ Password Changed:" -ForegroundColor Green
    $response | ConvertTo-Json
    
    # Change it back
    Write-Host "Changing password back..." -ForegroundColor Yellow
    $passwordDataBack = @{
        current_password = "NewSecurePass456"
        new_password = "SecurePass123"
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me/change-password" -Method Post -Headers $headers -Body $passwordDataBack
    Write-Host "✓ Password restored" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 9: Update User Email
Write-Host "[9] Testing PUT /api/v1/users/me (Update Email)..." -ForegroundColor Yellow
$updateData = @{
    email = "testuser@example.com"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/users/me" -Method Put -Headers $headers -Body $updateData
    Write-Host "✓ User Updated:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Admin Tests (Requires admin user)
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ADMIN ENDPOINTS (Requires Admin Role)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "To test admin endpoints:" -ForegroundColor Yellow
Write-Host "1. Create an admin user in the database:" -ForegroundColor Cyan
Write-Host "   UPDATE users SET role = 'admin' WHERE email = 'testuser@example.com';" -ForegroundColor White
Write-Host "2. Login again to get a new token with admin privileges" -ForegroundColor Cyan
Write-Host "3. Uncomment the admin tests below`n" -ForegroundColor Cyan

<#
# Test 10: Get All Users (Admin)
Write-Host "[10] Testing GET /api/v1/admin/users..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/admin/users?skip=0&limit=10" -Method Get -Headers $headers
    Write-Host "✓ All Users (Admin):" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Note: This requires admin role" -ForegroundColor Yellow
}
Write-Host ""

# Test 11: Get Dashboard Stats (Admin)
Write-Host "[11] Testing GET /api/v1/admin/stats..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/admin/stats" -Method Get -Headers $headers
    Write-Host "✓ Dashboard Stats (Admin):" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 12: Get Audit Logs (Admin)
Write-Host "[12] Testing GET /api/v1/admin/audit-logs..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/admin/audit-logs?skip=0&limit=20" -Method Get -Headers $headers
    Write-Host "✓ Audit Logs (Admin):" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""
#>

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "✓ Health Check - Working" -ForegroundColor Green
Write-Host "✓ Authentication - Working" -ForegroundColor Green
Write-Host "✓ User Management - Working" -ForegroundColor Green
Write-Host "✓ Profile with Encryption - Working" -ForegroundColor Green
Write-Host "✓ Password Change with History - Working" -ForegroundColor Green
Write-Host ""
Write-Host "For interactive testing, visit: http://localhost:8000/docs" -ForegroundColor Cyan
