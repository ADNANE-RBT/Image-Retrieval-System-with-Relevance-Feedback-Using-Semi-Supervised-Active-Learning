import { Component } from '@angular/core';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from '../../components/navbar/navbar.component';

@Component({
  selector: 'app-main-page',
  imports: [SidebarComponent, RouterOutlet, NavbarComponent],
  templateUrl: './main-page.component.html',
  styles: ``
})
export class MainPageComponent {

}
