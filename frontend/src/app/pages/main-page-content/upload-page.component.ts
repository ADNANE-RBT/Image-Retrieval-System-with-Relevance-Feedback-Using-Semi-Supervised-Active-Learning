import { Component, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImageService } from '../../services/image.service'; 
import { Router } from '@angular/router';


interface CheckboxGroup {
  id: string;
  label: string;
  value: string;
}

@Component({
  selector: 'app-upload-page',
  imports: [CommonModule],
  standalone: true,
  templateUrl: './upload-page.component.html',
  styles: ``
})
export class UploadpageComponent {
  uploadedImageUrl: string | null = null;
  selectedFile: File | null = null;
  selectedCategory: string | null = null;

  @ViewChild('fileInput') fileInputRef!: ElementRef;

  checkboxGroups: CheckboxGroup[] = [
    { id: 'checkbox-08-1', label: 'Grass', value: 'aGrass' },
    { id: 'checkbox-08-2', label: 'Field', value: 'bField' },
    { id: 'checkbox-08-3', label: 'Industry', value: 'cIndustry' },
    { id: 'checkbox-08-4', label: 'River/Lake', value: 'dRiverLake' },
    { id: 'checkbox-08-5', label: 'Forest', value: 'eForest' },
    { id: 'checkbox-08-6', label: 'Resident', value: 'fResident' },
    { id: 'checkbox-08-7', label: 'Parking', value: 'gParking' },
  ];

  constructor(private imageService: ImageService, private router: Router) {}

  // Handle file input change
  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        this.uploadedImageUrl = reader.result as string;
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  // Handle category selection
  onCategoryChange(event: Event, value: string): void {
    const input = event.target as HTMLInputElement;
    if (input.checked) {
      this.selectedCategory = value;
    } else if (this.selectedCategory === value) {
      this.selectedCategory = null; 
    }
  }

  uploadImage(): void {
    if (!this.selectedFile || !this.selectedCategory) {
      alert('Please select an image and a category before submitting.');
      return;
    }

    this.imageService.uploadImage(this.selectedFile, this.selectedCategory).subscribe({
      next: (response) => {
        console.log('Image uploaded successfully:', response);
        this.resetForm();
        const imageId = response._id;
        this.router.navigate([`/home/image/${imageId}`]);
      },
      error: (err) => {
        console.error('Error uploading image:', err);
        alert('Error uploading image. Please try again.');
      },
    });
  }

  resetForm(): void {
    this.uploadedImageUrl = null;
    this.selectedFile = null;
    this.selectedCategory = null;
    if (this.fileInputRef) {
      this.fileInputRef.nativeElement.value = '';
    }
  }
}
