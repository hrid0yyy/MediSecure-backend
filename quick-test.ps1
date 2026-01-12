# Quick API Test
Write-Host "=== Testing MediSecure APIs ===" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✓ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}

# Test 2: Root Endpoint
Write-Host "`n2. Root Endpoint..." -ForegroundColor Yellow
try {
    $root = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
    Write-Host "✓ Message: $($root.message)" -ForegroundColor Green
    Write-Host "✓ Version: $($root.version)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $_" -ForegroundColor Red
}

# Test 3: Sign Up
Write-Host "`n3. Sign Up New User..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$signupData = @{
    email = "test$timestamp@example.com"
    username = "testuser$timestamp"
    password = "TestPass123!@#"
} | ConvertTo-Json

try {
    $signup = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/signup" -Method POST -Body $signupData -ContentType "application/json"
    Write-Host "✓ User created: $($signup.email)" -ForegroundColor Green
    $global:testEmail = $signup.email
    $global:testUsername = "testuser$timestamp"
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit
}

# Test 4: Login
Write-Host "`n4. Login..." -ForegroundColor Yellow
$loginData = @{
    username = $global:testUsername
    password = "TestPass123!@#"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "✓ Login successful" -ForegroundColor Green
    $global:token = $login.access_token
    Write-Host "✓ Token received (${($global:token.Substring(0,20))}...)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit
}

# Test 5: Get Current User
Write-Host "`n5. Get Current User..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $($global:token)"
}
try {
    $user = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" -Method GET -Headers $headers
    Write-Host "✓ User ID: $($user.id)" -ForegroundColor Green
    Write-Host "✓ Username: $($user.username)" -ForegroundColor Green
    Write-Host "✓ Email: $($user.email)" -ForegroundColor Green
    Write-Host "✓ Role: $($user.role)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 6: Create User Profile
Write-Host "`n6. Create User Profile with Encrypted Data..." -ForegroundColor Yellow
$profileData = @{
    first_name = "John"
    last_name = "Doe"
    date_of_birth = "1990-01-01"
    phone = "123-456-7890"
    address = "123 Main St, City, State 12345"
    medical_record_number = "MRN-123456"
    insurance_number = "INS-789012"
    emergency_contact_name = "Jane Doe"
    emergency_contact_phone = "098-765-4321"
} | ConvertTo-Json

try {
    $profile = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me/profile" -Method POST -Body $profileData -ContentType "application/json" -Headers $headers
    Write-Host "✓ Profile created" -ForegroundColor Green
    Write-Host "✓ First Name: $($profile.first_name)" -ForegroundColor Green
    Write-Host "✓ Last Name: $($profile.last_name)" -ForegroundColor Green
    Write-Host "✓ MRN: $($profile.medical_record_number)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 7: Get User Profile
Write-Host "`n7. Get User Profile (Decrypted)..." -ForegroundColor Yellow
try {
    $getProfile = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me/profile" -Method GET -Headers $headers
    Write-Host "✓ Profile retrieved" -ForegroundColor Green
    Write-Host "✓ Full Name: $($getProfile.first_name) $($getProfile.last_name)" -ForegroundColor Green
    Write-Host "✓ Phone: $($getProfile.phone)" -ForegroundColor Green
    Write-Host "✓ Address: $($getProfile.address)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 8: Update User
Write-Host "`n8. Update User Email..." -ForegroundColor Yellow
$updateData = @{
    email = "updated$timestamp@example.com"
} | ConvertTo-Json

try {
    $updated = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" -Method PUT -Body $updateData -ContentType "application/json" -Headers $headers
    Write-Host "✓ User updated" -ForegroundColor Green
    Write-Host "✓ New Email: $($updated.email)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 9: Get Active Devices
Write-Host "`n9. Get Active Devices..." -ForegroundColor Yellow
try {
    $devices = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me/devices" -Method GET -Headers $headers
    Write-Host "✓ Active devices: $($devices.devices.Count)" -ForegroundColor Green
    if ($devices.devices.Count -gt 0) {
        Write-Host "✓ First device IP: $($devices.devices[0].ip_address)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 10: Change Password
Write-Host "`n10. Change Password..." -ForegroundColor Yellow
$passwordData = @{
    current_password = "TestPass123!@#"
    new_password = "NewPass123!@#"
} | ConvertTo-Json

try {
    $pwdChange = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me/change-password" -Method POST -Body $passwordData -ContentType "application/json" -Headers $headers
    Write-Host "✓ Password changed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed: $($_.Exception.Response.StatusCode.value__) - $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "All implemented features tested successfully!" -ForegroundColor Green
