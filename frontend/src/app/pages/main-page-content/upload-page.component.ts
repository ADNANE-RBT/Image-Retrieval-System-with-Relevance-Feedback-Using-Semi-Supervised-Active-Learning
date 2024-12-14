import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UploadbuttonComponent } from '../../components/buttons/upload-button/upload-button.component';
import { ImageUploadService } from '../../services/image-upload.service';
// import { MiniSidebarComponent } from '../../components/mini-sidebar/mini-sidebar.component';
import { GroupCheckBoxComponent } from '../../components/group-check-box/group-check-box.component';

@Component({
  selector: 'app-upload-page',
  imports: [CommonModule, UploadbuttonComponent, GroupCheckBoxComponent],
  standalone: true,
  templateUrl: './upload-page.component.html',
  styles: ``
})
export class UploadpageComponent {
  uploadedImageUrl: string | null = null;

  constructor(private imageUploadService: ImageUploadService) {
    this.imageUploadService.currentImage$.subscribe((imageUrl) => {
      this.uploadedImageUrl = imageUrl;
    });
  }
}
