import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Login } from './login.model';
import { isNullOrUndefined } from 'util';
import { MatDialog } from '@angular/material';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { ToastrService } from 'ngx-toastr';
import { customToaster } from "../_helper/toaster";
import * as jwt_decode from 'jwt-decode';


@Component({
  selector: "app-login",
  templateUrl: "./login.component.html",
  styleUrls: ["./login.component.css"]
})
export class LoginComponent implements OnInit {
  url = environment.apiUrl;
  public loginMessage = "";
  usermodel = new Login();
  loading = false;
  hide = true;
  
  constructor(
    private dialog: MatDialog,
    private http: HttpClient,
    private router: Router,
    private currentRoute: ActivatedRoute,
    private toastr: ToastrService
  ) {}
  ngOnInit() {
    this.toastr.clear();

    if (isNullOrUndefined(sessionStorage.getItem("accessToken"))) {
      this.router.navigateByUrl("/login");
    } else {
      this.router.navigateByUrl("/home/dashboard");
    }
  }
  
  loginuser() {
    this.loading = true;
    var data = this.usermodel;
    this.http.post(this.url + "user/login/", data).subscribe(
      (res: any) => {
        sessionStorage.setItem("accessToken", res.access);
        var decoded = jwt_decode(res.access); 
        sessionStorage.setItem("role", decoded.role);
        this.router.navigateByUrl("/home/dashboard");
        this.loginMessage = "";
      },
      error => {
        sessionStorage.removeItem("accessToken");
        this.router.navigateByUrl("/login");
        this.loginMessage = "Invalid Credentials";
        this.loading = false;
      }
    );
  }
}
