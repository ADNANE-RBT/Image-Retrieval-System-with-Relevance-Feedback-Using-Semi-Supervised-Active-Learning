import { Component } from '@angular/core';
import { ImageEditorComponent } from '../../components/image-editor-component/image-editor-component.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-edit-page',
  imports: [ImageEditorComponent, CommonModule],
  templateUrl: './edit-page.component.html',
  styles: ``
})
export class EditPageComponent {
  processedImageUrl: string | null = null;

  onImageProcessed(imageBlob: Blob) {
    this.processedImageUrl = URL.createObjectURL(imageBlob);
  }
}
