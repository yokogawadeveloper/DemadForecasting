import { ErrorHandler, Injectable } from "@angular/core";
import { Router } from "@angular/router";

@Injectable()
export class CustomErrorHandlerService {
  constructor(private router: Router) {}

  handleError(error) {
    if (error.status === 401) {
      sessionStorage.removeItem("accessToken");
      this.router.navigateByUrl("/login");
      return "Session timeout";
    } else if (error.status === 400) {
      return error.error.message;
    } else if (error.status === 500) {
      return "Internal server error !!!";
    } else {
      return "Connection error !!!";
    }
  }
  handleErrorDashboard(error) {
    if (error.status === 401) {
      sessionStorage.removeItem("accessToken");
      this.router.navigateByUrl("/login");
      return "Session timeout";
    } else if (error.status === 400) {
      return error.error.message;
    } else if (error.status === 500) {
      return "Internal server error !!!";
    } else {
      return "Connection error !!!";
    }
  }
}
