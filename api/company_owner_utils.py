from .models import AppUser, Company


def is_company_owner(user):
    """
    Check if a user is a company owner
    """
    return user and user.is_authenticated and user.company is not None


def get_company_owner_stats(company_id=None):
    """
    Get statistics about company owners
    """
    stats = {
        'total_company_owners': AppUser.objects.filter(company__isnull=False).count(),
        'total_companies_with_owners': Company.objects.filter(representatives__isnull=False).distinct().count(),
        'total_companies': Company.objects.count(),
    }
    
    if company_id:
        company = Company.objects.get(id=company_id)
        stats['company_name'] = company.name
        stats['company_representatives'] = company.representatives.count()
    
    return stats
