import { Component } from '@angular/core';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-main-page',
  imports: [SidebarComponent, RouterOutlet],
  templateUrl: './main-page.component.html',
  styles: ``
})
export class MainPageComponent {

}
