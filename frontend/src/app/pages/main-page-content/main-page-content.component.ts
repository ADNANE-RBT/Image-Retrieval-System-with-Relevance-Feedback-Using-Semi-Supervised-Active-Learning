import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UploadbuttonComponent } from '../../components/buttons/upload-button/upload-button.component';
import { ImageUploadService } from '../../services/image-upload.service';
import { MiniSidebarComponent } from '../../components/mini-sidebar/mini-sidebar.component';

@Component({
  selector: 'app-main-page-content',
  imports: [CommonModule, UploadbuttonComponent, MiniSidebarComponent],
  standalone: true,
  templateUrl: './main-page-content.component.html',
  styles: ``
})
export class MainPageContentComponent {
  uploadedImageUrl: string | null = null;

  constructor(private imageUploadService: ImageUploadService) {
    this.imageUploadService.currentImage$.subscribe((imageUrl) => {
      this.uploadedImageUrl = imageUrl;
    });
  }
}
