import { Component } from '@angular/core';
import { UploadbuttonComponent } from '../buttons/upload-button/upload-button.component';
import { RouterModule } from '@angular/router';
@Component({
  selector: 'app-sidebar',
  standalone: true,

  imports: [UploadbuttonComponent, RouterModule],
  templateUrl:'./sidebar.component.html',
  styles: ``
})
export class SidebarComponent {

}
