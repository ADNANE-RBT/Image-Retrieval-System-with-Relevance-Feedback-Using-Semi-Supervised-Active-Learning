import { Component } from '@angular/core';
// import { UploadbuttonComponent } from '../buttons/upload-button/upload-button.component';
import {  RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
// import { CommonModule } from '@angular/common';
@Component({
  selector: 'app-sidebar',
  standalone: true,

  imports: [ RouterModule, CommonModule ],
  templateUrl:'./sidebar.component.html',
  styles: ``
})
export class SidebarComponent {
  // constructor(public router: RouterModule) {}
}
