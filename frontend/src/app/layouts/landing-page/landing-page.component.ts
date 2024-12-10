import { Component } from '@angular/core';
import { NavbarComponent } from '../../components/navbar/navbar.component';
import { RouterOutlet } from '@angular/router';
 

@Component({
  selector: 'app-landing-page',
  imports: [NavbarComponent, RouterOutlet],
  templateUrl: './landing-page.component.html',
  styles: ``
})
export class LandingPageComponent {

}
