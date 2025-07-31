# Building Search and Filter Guide

This document explains how to use the filtering, searching, and sorting capabilities for buildings in the API.

## API Endpoint

All filtering and searching is done on the Buildings endpoint:
```
GET /api/buildings/
```

## Filtering Options

You can filter buildings using query parameters:

### Filter by Company

```
GET /api/buildings/?company=1
```

This returns all buildings belonging to the company with ID 1.

### Filter by Company Name

```
GET /api/buildings/?company_name=real
```

This returns all buildings belonging to companies with "real" in their name.

### Filter by Floor Count

```
GET /api/buildings/?floors_count=5
```

This returns all buildings with exactly 5 floors.

### Filter by Floor Count Range

```
GET /api/buildings/?min_floors=3&max_floors=10
```

This returns all buildings with 3 to 10 floors.

### Filter by Flat Count

```
GET /api/buildings/?flats_count=20
```

This returns all buildings with exactly 20 flats.

### Filter by Flat Count Range

```
GET /api/buildings/?min_flats=10&max_flats=50
```

This returns all buildings with 10 to 50 flats.

### Filter by Location/Address

```
GET /api/buildings/?location=downtown
```

This returns all buildings with "downtown" in their address.

### Filter by Name Contains

```
GET /api/buildings/?name_contains=plaza
```

This returns all buildings with "plaza" in their name.

### Combining Filters

You can combine multiple filters:

```
GET /api/buildings/?company=1&floors_count=5
```

This returns buildings that belong to company 1 AND have 5 floors.

## Search Capabilities

You can search across building name, address, and description:

```
GET /api/buildings/?search=central
```

This will return all buildings where "central" appears in the name, address, or description.

## Sorting Options

You can sort the results using the `ordering` parameter:

### Sort by Name

```
GET /api/buildings/?ordering=name
```

For descending order:
```
GET /api/buildings/?ordering=-name
```

### Sort by Company Name

```
GET /api/buildings/?ordering=company__name
```

### Sort by Floor Count

```
GET /api/buildings/?ordering=floors_count
```

### Sort by Flat Count

```
GET /api/buildings/?ordering=flats_count
```

## Combining Search, Filter and Sort

You can combine all options:

```
GET /api/buildings/?company=1&search=central&ordering=-floors_count
```

This returns buildings that:
- Belong to company 1
- Have "central" in their name, address, or description
- Are ordered by floor count in descending order

## Pagination

Results are paginated. You can use:

```
GET /api/buildings/?page=2
```

To get the second page of results.

## Notes for Company Owners

Company owners will automatically see only buildings for their own company, regardless of the filters applied.
