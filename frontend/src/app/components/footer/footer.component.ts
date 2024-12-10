import { Component, OnInit } from "@angular/core";

@Component({
  selector: "app-footer",
  standalone: true,
  templateUrl:'./footer.component.html'
})
export class FooterComponent implements OnInit {
  date = new Date().getFullYear();
  constructor() {}

  ngOnInit(): void {}
}
