import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ImageService, Image } from '../../services/image.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-image-view',
  imports: [],
  standalone: true,
  templateUrl: './image-view.component.html',
  styles: ``
})
export class ImageViewComponent implements OnInit {
  image: Image | null = null;
  errorMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private imageService: ImageService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    console.log('Image ID from route:', id); // Log the ID
  
    if (id) {
      this.fetchImageById(id);
    }
  }
  
  fetchImageById(id: string): void {
    this.imageService.getImageById(id).subscribe({
      next: (data) => {
        console.log('Fetched image data:', data); 
        this.image = data; 
      },
      error: (err) => {
        console.error('Error fetching image:', err); 
        this.errorMessage = `Error fetching image: ${err.message}`;
      }
    });
  }
}
