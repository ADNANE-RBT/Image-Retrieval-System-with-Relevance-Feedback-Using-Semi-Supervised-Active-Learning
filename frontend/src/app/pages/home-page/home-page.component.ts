import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImageService, Image } from '../../services/image.service'; // Adjust import path as needed

interface CheckboxGroup {
  id: string;
  label: string;
  value: string;
}

@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [
    CommonModule,
  ],
  templateUrl: './home-page.component.html',
})
export class HomePageComponent implements OnInit {
  checkboxGroups: CheckboxGroup[] = [
    { id: 'checkbox-08-1', label: 'Grass', value: 'aGrass' },
    { id: 'checkbox-08-2', label: 'Field', value: 'bField' },
    { id: 'checkbox-08-3', label: 'Industry', value: 'cIndustry' },
    { id: 'checkbox-08-4', label: 'River/Lake', value: 'dRiverLake' },
    { id: 'checkbox-08-5', label: 'Forest', value: 'eForest' },
    { id: 'checkbox-08-6', label: 'Resident', value: 'fResident' },
    { id: 'checkbox-08-7', label: 'Parking', value: 'gParking' },
  ];

  images: Image[] = [];
  selectedCategories: string[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(private imageService: ImageService) {}

  ngOnInit() {
    this.loadImages();
  }

  // Method to handle checkbox changes
  onCategoryChange(event: Event, category: string) {
    const checkbox = event.target as HTMLInputElement;
    
    if (checkbox.checked) {
      this.selectedCategories.push(category);
    } else {
      this.selectedCategories = this.selectedCategories.filter(cat => cat !== category);
    }

    this.loadImages();
  }

  // Load images based on selected categories
  loadImages() {
    this.isLoading = true;
    this.errorMessage = '';

    // If no categories selected, fetch all images
    const categoriesToFetch = this.selectedCategories.length > 0 
      ? this.selectedCategories 
      : this.checkboxGroups.map(group => group.value);

    this.imageService.getImagesByCategory(categoriesToFetch)
      .subscribe({
        next: (images) => {
          this.images = images;
          this.isLoading = false;
        },
        error: (error) => {
          this.errorMessage = 'Failed to load images';
          this.isLoading = false;
          console.error('Error loading images:', error);
        }
      });
  }

  // Optional: method to handle image click (e.g., open in modal)
  onImageClick(image: Image) {
    // Implement image view logic if needed
    console.log('Image clicked:', image);
  }
}