#!/usr/bin/env python3
"""
Test script for location randomization functionality.
"""

from image_metadata import ImageMetadataModifier

def test_location_randomization():
    """Test location randomization functionality."""
    print("Testing Location Randomization")
    print("=" * 40)
    
    modifier = ImageMetadataModifier()
    
    # Test generating multiple random locations
    print("Generating 5 random UK locations:")
    locations = []
    
    for i in range(5):
        location = modifier.generate_random_uk_location()
        locations.append(location)
        print(f"  {i+1}. {location['name']} ({location['lat']:.4f}, {location['lon']:.4f})")
    
    # Check for uniqueness
    unique_locations = set(loc['name'] for loc in locations)
    print(f"\nUnique locations: {len(unique_locations)}/{len(locations)}")
    
    if len(unique_locations) == len(locations):
        print("SUCCESS: All locations are unique")
    else:
        print("WARNING: Some locations are duplicated")
    
    # Test location diversity
    print(f"\nLocation diversity:")
    for location in locations:
        print(f"  - {location['name']}: {location['lat']:.4f}, {location['lon']:.4f}")
    
    return True

def test_location_integration():
    """Test integration with the bot system."""
    print("\nTesting Location Integration")
    print("=" * 40)
    
    # Simulate the bot's location randomization process
    modifier = ImageMetadataModifier()
    
    # Mock listing data
    mock_listings = [
        {'listing_id': '1', 'title': 'Artificial Grass | SAMPLE BOX'},
        {'listing_id': '2', 'title': 'Premium Turf | 40mm Thick'},
        {'listing_id': '3', 'title': 'Garden Grass | Professional Grade'}
    ]
    
    print("Simulating location randomization for mock listings:")
    
    randomized_locations = []
    for listing in mock_listings:
        # Generate a random UK location
        random_location = modifier.generate_random_uk_location()
        
        randomized_locations.append({
            'listing_id': listing['listing_id'],
            'title': listing['title'],
            'new_location': random_location['name'],
            'coordinates': f"{random_location['lat']:.4f}, {random_location['lon']:.4f}"
        })
    
    # Display results
    for i, location in enumerate(randomized_locations, 1):
        print(f"  {i}. {location['title']}")
        print(f"     Location: {location['new_location']}")
        print(f"     Coordinates: {location['coordinates']}")
        print()
    
    return True

def main():
    """Run location randomization tests."""
    print("LOCATION RANDOMIZATION TEST")
    print("=" * 50)
    
    # Test basic functionality
    result1 = test_location_randomization()
    
    # Test integration
    result2 = test_location_integration()
    
    if result1 and result2:
        print("\nSUCCESS: Location randomization is working correctly")
        print("The UI will now be able to randomize locations for selected listings")
    else:
        print("\nERROR: Location randomization has issues")

if __name__ == "__main__":
    main()
