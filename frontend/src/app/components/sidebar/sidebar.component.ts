import { Component } from '@angular/core';
import { UploadbuttonComponent } from '../buttons/upload-button/upload-button.component';
@Component({
  selector: 'app-sidebar',
  standalone: true,

  imports: [UploadbuttonComponent],
  templateUrl:'./sidebar.component.html',
  styles: ``
})
export class SidebarComponent {

}
