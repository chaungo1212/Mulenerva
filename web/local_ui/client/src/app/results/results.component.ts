/* This file was created by Patrick Shane McClintock in April 2018 for the Mulenerva Project. */

import { Component, OnInit } from '@angular/core';
import { Http, Response, Headers, URLSearchParams, RequestOptions } from '@angular/http';

import { QueryService } from '../query.service';

import * as images from '../../assets/images';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {

  public timerToken: any;
  public results: any[] = [];
  public e_result: any;
  public expanded: boolean = false;
  public showing_results: boolean = false;

  private base_url = "http://mulenerva.bitwisehero.com:5001/";
  private subject: string = "";
  private query: string = "";
  private filter: boolean[] = [true, true, true, true];
  private tags: string[] = ['Tag10', 'Tag20', 'Tag30'];
  private imgurl: string = images.defaultimg();
  private shortdescription: string = "This is a short description!";

  constructor(private qs: QueryService, private http: Http) {
    this.timerToken = setInterval(() => { this.timerCallback() }, 500);
    this.search(this.subject, this.query);
  }

  ngOnInit() {

  }

  //Every 500ms, this function is called.  Use it to update the results.
  private timerCallback(): void {
    if (this.qs.isUpdated()) {
      this.subject = this.qs.getSubject();
      this.query = this.qs.getQuery();
      this.filter = this.qs.getFilter();
      this.expanded = false;
      this.showing_results = false;

      if ((this.filter[2] || this.filter[3]) && (this.filter[0] || this.filter[1])) {
        this.search(this.subject, this.query);
      } else {
        this.results = [];
      }
    }
  }


  public search(subject?: string, title?: string): void {

    let url = this.base_url + "search";

    let searchParams = new URLSearchParams();
    searchParams.append('genre', subject);
    searchParams.append('title', title);
    if (this.filter[1]) {
      searchParams.append('type', 'video');
    }
    if (this.filter[0]) {
      searchParams.append('type', 'document');
    }
    if (!this.filter[2]) {
      searchParams.append('isRequested', 'false');
    }
    if (!this.filter[3]) {
      searchParams.append('isAvailable', 'false');
    }

    let tags = title.split(" ");
    for (let tag of tags) {
      searchParams.append('tags', tag.toLowerCase());
    }

    let options = new RequestOptions({ params: searchParams });
    try {
      this.http.get(url, options).subscribe(res => {
        console.log(res);
        console.log("Got content: ");
        console.log(res.json());
        this.results = res.json();
      }, error => console.error(error));
    }
    catch (any) {
      //Handle errors here.
      console.log("Search failed.");
    }
  }

  private getImage(result: any): any {
    //return this.imgurl;
    if (result.thumbnail === null) return this.imgurl;
    let id = result._id.$oid;
    let url = this.base_url + "image/" + id;

    //console.log("Image for result of id " + id + ": " + url);

    return url;
  }

  private expansion(result: any): void {
    this.e_result = result;
    this.expanded = true;
  }

  private unexpand(): void {
    this.expanded = false;
    this.e_result = null;
  }

  private get_result(option: string): void {
    let url = this.base_url + "metadata/";
    if (option === "next") {
      url += this.e_result.next_key;
    } else if (option === "prev") {
      url += this.e_result.previous_key;
    }

    let searchParams = new URLSearchParams();

    let options = new RequestOptions({ params: searchParams });
    try {
      this.http.get(url, options).subscribe(res => {
        console.log(res);
        console.log("Got next content:");
        console.log(res.json());
        this.e_result = res.json();
      }, error => console.error(error));
    }
    catch (any) {
      //Handle errors here.
      console.log("No next content available.");
    }
  }

  request(): void {
    let url = this.base_url + "request";
    let searchParams = new URLSearchParams();
    searchParams.append("id", this.e_result._id.$oid);

    let options = new RequestOptions({ params: searchParams });
    try {
      this.http.get(url, options).subscribe(res => {
        console.log(res);
        console.log("Requested content:")
        console.log(res.json());
        this.e_result = res.json();
      }, error => console.error(error));
    }
    catch (any) {
      //Handle errors here.
      console.log("No next content available.");
    }
  }

  view(): string {
    return this.base_url + "content/" + this.e_result._id.$oid;
  }
}
