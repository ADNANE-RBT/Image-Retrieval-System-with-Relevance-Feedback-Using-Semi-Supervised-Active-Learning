import { Component, OnInit } from "@angular/core";

@Component({
  selector: 'app-navbar',
  standalone: true,

  imports: [],
  templateUrl:'./navbar.component.html',
  styles: ``
})
export class NavbarComponent implements OnInit {
  navbarOpen = false;

  constructor() {}

  ngOnInit(): void {}

  setNavbarOpen() {
    this.navbarOpen = !this.navbarOpen;
  }
}
