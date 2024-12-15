// image-view.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ImageService, Image } from '../../services/image.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-image-view',
  imports: [CommonModule],
  standalone: true,
  templateUrl: './image-view.component.html',
  styles: ``
})
export class ImageViewComponent implements OnInit {
  image: Image | null = null;
  errorMessage: string | null = null;
  descriptorImage: string | null = null;
  isLoadingDescriptors: boolean = false;
  private flaskApiUrl = 'http://localhost:5001'; // Flask backend URL

  constructor(
    private route: ActivatedRoute,
    private imageService: ImageService,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.fetchImageById(id);
    }
  }
  
  fetchImageById(id: string): void {
    this.imageService.getImageById(id).subscribe({
      next: (data) => {
        this.image = data;
        if (data.path) {
          console.log('Original image path:', data.path);
          this.fetchDescriptors(data.path);
        }
      },
      error: (err) => {
        console.error('Error fetching image:', err);
        this.errorMessage = `Error fetching image: ${err.message}`;
      }
    });
  }



  fetchDescriptors(imagePath: string): void {
    this.isLoadingDescriptors = true;
    this.errorMessage = null;
    imagePath=imagePath.replace('http://localhost:5000/Dataset/RSSCN7-master', '');
    console.log('Formatted path for Flask:', imagePath);

    // Set up headers for debugging
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    const requestBody = { image_path: imagePath };
    console.log('Request body:', requestBody);
    console.log('Request URL:', `${this.flaskApiUrl}/descriptors`);

    // Make the request
    this.http.post('http://localhost:5001/descriptors', { image_path: imagePath }, { responseType: 'blob' })
    .subscribe({
      next: (response: Blob) => {
        const objectURL = URL.createObjectURL(response); // Convert Blob to object URL
        this.descriptorImage = objectURL; // Bind the object URL to an <img> element
        this.isLoadingDescriptors = false;
      },
      error: (error) => {
        console.error('Error fetching descriptors:', error);
        this.errorMessage = 'Failed to load image descriptors.';
        this.isLoadingDescriptors = false;
      }
    });
  
}


  downloadDescriptors(): void {
    if (this.descriptorImage) {
      const link = document.createElement('a');
      link.href = this.descriptorImage;
      link.download = 'descriptor_visualization.png';
      link.click();
    }
  }

  ngOnDestroy(): void {
    if (this.descriptorImage) {
      URL.revokeObjectURL(this.descriptorImage);
    }
  }
}