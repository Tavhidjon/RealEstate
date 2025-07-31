# Company Owner System Implementation

We've successfully implemented a system where only admin users can create company owner accounts, and company owners can log in to manage their company's resources.

## Key Features Added

1. **Company Owner Registration (Admin-Only)**
   - New endpoint: `/api/auth/register-company-owner/`
   - Only accessible to users with admin privileges
   - Links users to companies during registration

2. **Company Owner Authentication**
   - Enhanced JWT tokens to include company information
   - Added `is_company_owner` flag to user authentication

3. **Company Owner Management**
   - Admin endpoint to list all company owners: `/api/auth/company-owners/`
   - Can filter company owners by company ID

4. **Permission Classes**
   - Added new permission classes:
     - `IsCompanyOwner`: Only allows authenticated users with company association
     - `IsCompanyOwnerOrAdmin`: Allows either company owners or admins
     - `IsCompanyOwnerForCompanyBuildings`: Custom permission for building management

5. **Building Management for Company Owners**
   - Company owners can create, view, update, and delete buildings for their company
   - Buildings created by company owners are automatically associated with their company
   - Company owners can only see and modify buildings for their own company

6. **Admin Panel Enhancements**
   - Added company owner statistics
   - Shows number of representatives per company

## How to Use

### Admin User Workflow:
1. Log in as an admin user
2. Create a company if it doesn't exist
3. Register a company owner via `/api/auth/register-company-owner/`
4. Assign the company owner to a company during registration

### Company Owner Workflow:
1. Log in using the credentials provided by the admin
2. The system automatically recognizes them as a company owner
3. They can manage resources related to their company

## Testing the Implementation

We've provided testing scripts to demonstrate the functionality:

### Creating a Company Owner (as Admin)

```bash
python create_company_owner.py [admin_email] [admin_password] [company_id]
```

### Creating a Building (as Company Owner)

```bash
python create_building.py [company_owner_email] [password] [building_name] [latitude] [longitude]
```

For more details, see the [Company Owner Guide](COMPANY_OWNER_GUIDE.md).
