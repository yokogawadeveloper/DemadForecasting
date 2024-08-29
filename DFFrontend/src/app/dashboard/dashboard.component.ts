import { Component, OnInit } from "@angular/core";
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders
} from "@angular/common/http";
import { environment } from "src/environments/environment";
import { Data } from "./dashboard.model";
import * as Chart from "chart.js";
import { CustomErrorHandlerService } from "../_helper/errorHandler";
import { Router } from "@angular/router";
import { customToaster } from "../_helper/toaster";
import { ToastrService } from "ngx-toastr";
import { CpaStockChartData } from '../_helper/cpaStockGraph';
import { ChartDataSets, ChartOptions, ChartType } from "chart.js";
import { inventoryGraph } from "../_helper/inventoryGraph";

@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.component.html",
  styleUrls: ["./dashboard.component.css"]
})

export class DashboardComponent implements OnInit {
  url = environment.apiUrl;
  p: number = 1;
  kanbanPg: number = 1;
  data;
  kanbanData;
  inventoryData;
  loading = true;
  loadingChart = true;
  loadingKanban = true;
  loadingInventory = true

  constructor(
    private httpService: HttpClient,
    private router: Router,
    private toastr: ToastrService
  ) { }

  ngOnInit() {
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };

    //get the data for alert table
    this.httpService.get(this.url + "alert/", httpOptions).subscribe(
      response => {
        this.loading = false;
        this.data = response;
      },
      (err: HttpErrorResponse) => {
        let erorHandler = new CustomErrorHandlerService(this.router);
        let myToaster = new customToaster(this.toastr);
        myToaster.showError(erorHandler.handleErrorDashboard(err));
        this.loading = false;
      }
    );

    // get data for cpa graph
    this.httpService.get<Data[]>(this.url + "cpastokechartdata/", httpOptions).subscribe(
      (res: {}) => {
        CpaStockChartData(res["context"]);
        this.loadingChart = false;
      },
      err => {
        let erorHandler = new CustomErrorHandlerService(this.router);
        let myToaster = new customToaster(this.toastr);
        myToaster.showError(erorHandler.handleErrorDashboard(err));
        this.loadingChart = false;
      }
    );

    //get the data for kanban table
    this.httpService.get(this.url + "kanban/", httpOptions).subscribe(
      response => {
        this.loadingKanban = false;
        this.kanbanData = response;
      },
      (err: HttpErrorResponse) => {
        let erorHandler = new CustomErrorHandlerService(this.router);
        let myToaster = new customToaster(this.toastr);
        myToaster.showError(erorHandler.handleErrorDashboard(err));
        this.loadingKanban = false;
      }
    );

    this.httpService.get(this.url + "inventory/", httpOptions).subscribe(
      response => {
        this.loadingInventory = false;
        inventoryGraph(response['context'])
        this.inventoryData = response['context'];
      },
      (err: HttpErrorResponse) => {
        let erorHandler = new CustomErrorHandlerService(this.router);
        let myToaster = new customToaster(this.toastr);
        myToaster.showError(erorHandler.handleErrorDashboard(err));
        this.loadingKanban = false;
      }
    );


  }

  //demo chart

  public barChartOptions: ChartOptions = {
    responsive: true
  };
  public barChartType: ChartType = 'bar';
  public barChartLegend = true;

  public barChartData: ChartDataSets[] = [
    { data: [10, 20, 30], label: 'KDP COST', type: 'line' },
    { data: [1, 2, 3], label: 'CPA COST', type: 'line' },

    { data: [20, 30, 40], label: 'CPA110Y', stack: 'a' },
    { data: [1, 2, 3], label: 'CPA430Y', stack: 'a' },
    { data: [1, 2, 3], label: 'CPA530Y', stack: 'a' },
  ];
  public barChartLabels: string[] = ['P', 'R', 'B'];

  public chartClicked({ event, active }: { event: MouseEvent, active: {}[] }): void {
    console.log(event, active);
  }

  public chartHovered({ event, active }: { event: MouseEvent, active: {}[] }): void {
    console.log(event, active);
  }

}
