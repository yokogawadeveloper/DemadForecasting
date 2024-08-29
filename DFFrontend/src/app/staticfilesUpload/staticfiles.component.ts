import { Component, OnInit } from "@angular/core";
import {
  Validators,
  FormGroup,
  FormBuilder,
  FormControl,
  FormControlName
} from "@angular/forms";
import {
  HttpClient,
  HttpHeaders,
  HttpErrorResponse
} from "@angular/common/http";
import { FileUploader } from "ng2-file-upload";
import { environment } from "src/environments/environment";
import { controllers } from "chart.js";
import { Router } from "@angular/router";
import { CustomErrorHandlerService } from "../_helper/errorHandler";
import { customToaster } from "../_helper/toaster";
import { ToastrService } from "ngx-toastr";
import {
  ConfirmDialogModel,
  ConfirmDialogComponent
} from "../confirm-dialog/confirm-dialog.component";
import { MatDialog } from "@angular/material";
import { NgxSpinnerService } from "ngx-spinner";

@Component({
  selector: "app-staticfiles",
  templateUrl: "./staticfiles.component.html",
  styleUrls: ["./staticfiles.component.css"]
})
export class StaticfilesComponent implements OnInit {
  public uploader: FileUploader = new FileUploader({ isHTML5: true });
  url = environment.apiUrl;
  result: string = "";
  projectedQty;
  consumedQty;
  quantity;
  dates;

  constructor(
    private formBuilder: FormBuilder,
    private httpService: HttpClient,
    private router: Router,
    private toastr: ToastrService,
    public dialog: MatDialog,
    private spinner: NgxSpinnerService
  ) {}
  staticFiles: FormGroup;
  industry: FormGroup;

  ngOnInit() {
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    //get the data
    let myToaster = new customToaster(this.toastr);

    this.httpService.get<any>(this.url + "industrywise/", httpOptions).subscribe(
      response => {
        if(response.value == "false"){
          myToaster.showError(response.message);
        }
          this.quantity = response[0];
      },
      (err: HttpErrorResponse) => {
        let erorHandler = new CustomErrorHandlerService(this.router);
        myToaster.showError(erorHandler.handleErrorDashboard(err));
      }
    );

    // form group for normal static files
    this.staticFiles = this.formBuilder.group({
      LeadTimeCategoryPrice: new FormControl(""),
      final110e430e: new FormControl(""),
      final530e: new FormControl(""),
      finalPrediction: new FormControl(""),
      option110: new FormControl(""),
      option530: new FormControl(""),
      thresholdQty: new FormControl(""),
      unwanted: new FormControl(""),
      growthRate: new FormControl(""),
      customerWiseData: new FormControl(""),
      consumedQty: new FormControl(""),
      projectedQty: new FormControl(""),
      Forcast_Template : new FormControl("")
    });

    // form group for industry static files
    this.industry = this.formBuilder.group({
      growthRate: new FormControl(""),
      customerWiseData: new FormControl(""),
      consumedQty: new FormControl(""),
      projectedQty: new FormControl("")
    });

    // dates of static files
    this.httpService
      .get<any>(this.url + "datesofstaticfiles/", httpOptions)
      .subscribe(
        res => {
          this.dates = res;
        },
        err => {
          let erorHandler = new CustomErrorHandlerService(this.router);
          let myToaster = new customToaster(this.toastr);
          myToaster.showError(erorHandler.handleErrorDashboard(err));
        }
      );
  }

  staticFilesUpload() {
    this.spinner.show();
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    const formData = new FormData();
    formData.append(
      "LeadTimeCategoryPrice",
      this.staticFiles.get("LeadTimeCategoryPrice").value
    );
    formData.append(
      "final110e430e",
      this.staticFiles.get("final110e430e").value
    );
    formData.append("final530e", this.staticFiles.get("final530e").value);

    formData.append(
      "finalPrediction",
      this.staticFiles.get("finalPrediction").value
    );

    formData.append("option110", this.staticFiles.get("option110").value);
    formData.append("option530", this.staticFiles.get("option530").value);
    formData.append("thresholdQty", this.staticFiles.get("thresholdQty").value);
    formData.append("unwanted", this.staticFiles.get("unwanted").value);
    formData.append("growthRate", this.staticFiles.get("growthRate").value);
    formData.append(
      "customerWiseData",
      this.staticFiles.get("customerWiseData").value
    );
    formData.append(
      "consumedQty",
      (<HTMLInputElement>document.getElementById("consumedQty")).value
    );
    formData.append(
      "projectedQty",
      (<HTMLInputElement>document.getElementById("projectedQty")).value
    );
    formData.append(
      "Forcast_Template",
       this.staticFiles.get("Forcast_Template").value
    );

    this.httpService
      .post<any>(this.url + "staticfileupload/", formData, httpOptions)
      .subscribe(
        res => {
          let myToaster = new customToaster(this.toastr);
          myToaster.showSuccess(res.message);
          return this.spinner.hide();
        },
        err => {
          let erorHandler = new CustomErrorHandlerService(this.router);
          let myToaster = new customToaster(this.toastr);
          myToaster.showError(erorHandler.handleErrorDashboard(err));
          return this.spinner.hide();
        }
      );
  }
  // industry wise form development
  Industry() {
    this.spinner.show();
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    const formData = new FormData();
    formData.append("growthRate", this.industry.get("growthRate").value);
    formData.append(
      "customerWiseData",
      this.industry.get("customerWiseData").value
    );
    formData.append(
      "consumedQty",
      (<HTMLInputElement>document.getElementById("consumedQty")).value
    );
    formData.append(
      "projectedQty",
      (<HTMLInputElement>document.getElementById("projectedQty")).value
    );

    this.httpService
      .post<any>(this.url + "industrywise/", formData, httpOptions)
      .subscribe(
        res => {
          let myToaster = new customToaster(this.toastr);
          myToaster.showSuccess(res.message);
          return this.spinner.hide();
        },
        err => {
          let erorHandler = new CustomErrorHandlerService(this.router);
          let myToaster = new customToaster(this.toastr);
          myToaster.showError(erorHandler.handleErrorDashboard(err));
          return this.spinner.hide();
        }
      );
  }

  OnFileSelect(event, name) {
    const file = event.target.files[0];
    return this.staticFiles.get(name).setValue(file);
  }
  OnFileSelectIndustry(event, name) {
    const file = event.target.files[0];
    return this.industry.get(name).setValue(file);
  }
  confirmDialog(names): void {
    const message = `Are you sure you want to Upload ?`;

    const dialogData = new ConfirmDialogModel("Confirm Upload", message);

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      maxWidth: "500px",
      data: dialogData
    });

    dialogRef.afterClosed().subscribe(dialogResult => {
      this.result = dialogResult;
      if (dialogResult == true) {
        if (names == "staticfile") {
          this.staticFilesUpload();
          console.log("stat");
        } else if (names == "industry") {
          this.Industry();
          console.log("industry");
        }
      }
    });
  }
}
