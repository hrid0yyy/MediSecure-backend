# MediSecure API Testing Script
# This script tests the complete user flow including authentication, profile management, and device handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MediSecure API Testing Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$baseUrl = "http://localhost:8000"
$testEmail = "testuser_$(Get-Random -Minimum 1000 -Maximum 9999)@example.com"
$testPassword = "SecurePass123!@#"

Write-Host "Test Configuration:" -ForegroundColor Yellow
Write-Host "  Base URL: $baseUrl" -ForegroundColor Gray
Write-Host "  Test Email: $testEmail" -ForegroundColor Gray
Write-Host ""

# Helper function to display responses
function Show-Response {
    param($title, $response)
    Write-Host "✓ $title" -ForegroundColor Green
    Write-Host "  Response: " -ForegroundColor Gray -NoNewline
    Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor White
    Write-Host ""
}

function Show-Error {
    param($title, $error)
    Write-Host "✗ $title" -ForegroundColor Red
    Write-Host "  Error: $error" -ForegroundColor Gray
    Write-Host ""
}

# Test 1: Health Check
Write-Host "[1/12] Testing Health Check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Show-Response "Health Check" $health
} catch {
    Show-Error "Health Check Failed" $_.Exception.Message
    exit 1
}

# Test 2: Root Endpoint
Write-Host "[2/12] Testing Root Endpoint..." -ForegroundColor Cyan
try {
    $root = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Show-Response "Root Endpoint" $root
} catch {
    Show-Error "Root Endpoint Failed" $_.Exception.Message
}

# Test 3: User Signup
Write-Host "[3/12] Testing User Signup..." -ForegroundColor Cyan
$signupBody = @{
    email = $testEmail
    password = $testPassword
} | ConvertTo-Json

try {
    $signupResponse = Invoke-RestMethod -Uri "$baseUrl/auth/signup" -Method POST -Body $signupBody -ContentType "application/json"
    Show-Response "User Signup" $signupResponse
    
    Write-Host "⚠ INFO: Check the server console for the FALLBACK verification code!" -ForegroundColor Yellow
    Write-Host "  Email: $testEmail" -ForegroundColor Gray
    $verificationCode = Read-Host "  Enter the 6-digit verification code"
    Write-Host ""
} catch {
    Show-Error "Signup Failed" $_.Exception.Message
    exit 1
}

# Test 4: Email Verification
Write-Host "[4/12] Testing Email Verification..." -ForegroundColor Cyan
$verifyBody = @{
    email = $testEmail
    code = $verificationCode
} | ConvertTo-Json

try {
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/auth/verify-email" -Method POST -Body $verifyBody -ContentType "application/json"
    Show-Response "Email Verification" $verifyResponse
} catch {
    Show-Error "Email Verification Failed" $_.Exception.Message
    exit 1
}

# Test 5: User Login
Write-Host "[5/12] Testing User Login..." -ForegroundColor Cyan
$loginBody = @{
    email = $testEmail
    password = $testPassword
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Show-Response "User Login" $loginResponse
    
    Write-Host "  🔑 Token: $($token.Substring(0, 10))..." -ForegroundColor Magenta
    Write-Host ""
} catch {
    Show-Error "Login Failed" $_.Exception.Message
    exit 1
}

# Setup authorization header
$headers = @{
    "Authorization" = "Bearer $token"
}

# Test 6: Get Current User
Write-Host "[6/12] Testing Get Current User..." -ForegroundColor Cyan
try {
    $currentUser = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me" -Method GET -Headers $headers
    Show-Response "Current User Profile" $currentUser
} catch {
    Show-Error "Get Current User Failed" $_.Exception.Message
}

# Test 7: Create User Profile
Write-Host "[7/12] Testing Create User Profile..." -ForegroundColor Cyan
$profileBody = @{
    first_name = "John"
    last_name = "Doe"
    date_of_birth = "1990-01-01"
    phone = "+1-555-123-4567"
    address = "123 Main Street"
    medical_record_number = "MRN-12345"
    insurance_number = "INS-67890"
    emergency_contact_name = "Jane Doe"
    emergency_contact_phone = "+1-555-987-6543"
} | ConvertTo-Json

try {
    $profileResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me/profile" -Method POST -Body $profileBody -ContentType "application/json" -Headers $headers
    Show-Response "Create Profile" $profileResponse
} catch {
    Show-Error "Create Profile Failed" $_.Exception.Message
}

# Test 8: Get User Profile
Write-Host "[8/12] Testing Get User Profile..." -ForegroundColor Cyan
try {
    $profile = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me/profile" -Method GET -Headers $headers
    Show-Response "User Profile" $profile
} catch {
    Show-Error "Get Profile Failed" $_.Exception.Message
}

# Test 9: Get User Devices
Write-Host "[9/12] Testing Get User Devices..." -ForegroundColor Cyan
try {
    $devices = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me/devices" -Method GET -Headers $headers
    Show-Response "User Devices" $devices
} catch {
    Show-Error "Get Devices Failed" $_.Exception.Message
}

# Test 10: Update User
Write-Host "[10/12] Testing Update User..." -ForegroundColor Cyan
$updateBody = @{
    email = $testEmail
} | ConvertTo-Json

try {
    $updateResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me" -Method PUT -Body $updateBody -ContentType "application/json" -Headers $headers
    Show-Response "Update User" $updateResponse
} catch {
    Show-Error "Update User Failed" $_.Exception.Message
}

# Test 11: Change Password
Write-Host "[11/12] Testing Change Password..." -ForegroundColor Cyan
$newPassword = "NewPassword123!"
$passwordBody = @{
    current_password = $testPassword
    new_password = $newPassword
} | ConvertTo-Json

try {
    $passwordResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/users/me/change-password" -Method POST -Body $passwordBody -ContentType "application/json" -Headers $headers
    Show-Response "Change Password" $passwordResponse
    $testPassword = $newPassword
} catch {
    Show-Error "Change Password Failed" $_.Exception.Message
}

# Test 12: Login with New Password
Write-Host "[12/12] Testing Login with New Password..." -ForegroundColor Cyan
$newLoginBody = @{
    email = $testEmail
    password = $newPassword
} | ConvertTo-Json

try {
    $newLoginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $newLoginBody -ContentType "application/json"
    Show-Response "Login with New Password" $newLoginResponse
} catch {
    Show-Error "Login with New Password Failed" $_.Exception.Message
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tests Completed" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
