import { Component } from '@angular/core';
import { isNullOrUndefined } from 'util';
import { Router } from '@angular/router';

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"]
})
export class AppComponent {
  title = "NewappTest";
  constructor(
    private router: Router,
  ) {} 
  ngOnInit() {
    if (isNullOrUndefined(sessionStorage.getItem("accessToken"))) {
      return this.router.navigateByUrl("/login")
    } 
  }
}
