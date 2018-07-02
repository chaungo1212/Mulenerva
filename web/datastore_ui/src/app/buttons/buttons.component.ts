import { Component, OnInit } from '@angular/core';
import { QueryService } from '../query.service';
import {Http, Response, Headers, URLSearchParams, RequestOptions} from '@angular/http';
@Component({
  selector: 'app-buttons',
  templateUrl: './buttons.component.html',
  styleUrls: ['./buttons.component.css']
})
/*
    This code is written based on Patrick McClintock's code
*/
export class ButtonsComponent implements OnInit {
   // results: any;
    title: string = "";
    type: string = "";
    author: string = "";
    query: string = "" ;
    long_desc: string = "";
    short_desc: string ="";
    filter: boolean[] = [true, true, true, true];
    screen_to_show = 0;
    placeholder:  String = 'Enter Book Name!';
    placeholder1: String = 'Enter Author Name!';
    placeholder2: String = 'Long Description';
    placeholder3: String = 'Short Description';
    placeholder4: String = 'Enter Video Name';
    placeholder5: String = 'Enter Publisher';
    placeholder7: String = 'Short Description ';
    placeholder15: String = 'Long Description';
    placeholder8: String = 'New Author';
    placeholder9: String = 'New Name';
    placeholder10: String = 'New Short Desctiption';
    placeholder11: String = 'New Long Desctiption';
    $oid: string = "";
    results: any[] = [];
    e_result: any;
    open: boolean = false;
    document_selected: boolean = false;
    subject: string = 'Select Subject';
    base_url: String = 'http://mulenerva.bitwisehero.com:5002/';
    Subjects = ['Art', 'Biology', 'Chemistry', 'Computer Science', 'Engineering',
     'English', 'Geology', 'History', 'Mathematics', 'Physics', 'Spanish'];
    constructor(private qs: QueryService, private http: Http) {
        this.view();
    }
    ngOnInit() {}
    updateID(): void {
        this.$oid = (<HTMLInputElement>document.getElementById('title')).value;
        this.qs.setSubject(this.subject);
    }
    updateResults(result: any): void {
        this.e_result = result;
    }
    updateSubject(): void {
        this.subject = (<HTMLInputElement>document.getElementById('subject-dropdown')).value;
        this.qs.setSubject(this.subject);
    }
viewDoc(): void {
const addtype = (<HTMLInputElement>document.getElementById('Material-Dropdown')).value;
        if (addtype === 'Document') {
          this.screen_to_show = 5;
        } else if (addtype === 'Video') {
           this.screen_to_show = 6;
        }

        }
modify(): void {
    const addtype = (<HTMLInputElement>document.getElementById('Material-Dropdown')).value;
    if (addtype === 'Document') {
        this.screen_to_show = 9;
    } else if (addtype === 'Video') {
        this.screen_to_show = 10;
    } 
}
delete(): void {
    const addtype = (<HTMLInputElement>document.getElementById('Material-Dropdown')).value;
    if (addtype === 'Document') {
        this.screen_to_show = 13;
    } else if (addtype === 'Video') {
        this.screen_to_show = 14;
    }
}
viewbook():void {
    const addtype = (<HTMLInputElement>document.getElementById('viewbookbutton')).value;
    this.screen_to_show = 25;
}
view(): void {
    let url = this.base_url + "search";
    let searchParams = new URLSearchParams();
    let options = new RequestOptions({ params: searchParams });
    try {
      this.http.get(url, options).subscribe(res => {
        console.log(res);
        console.log(res.json());
        this.results = res.json();
      }, error => console.error(error));
    } catch (any) {
      console.log("View failed");
    }
}

  expansion(result: any): void {
    this.e_result = result;
    this.open = true;
  }

 unexpand(): void {
    this.open = false;
    this.e_result = null;
  }
  addbook(): void {
    const addtype = (<HTMLInputElement>document.getElementById('addbookbutton')).value;
    this.screen_to_show = 21;
  }
  addvid(): void {
    const addtype = (<HTMLInputElement>document.getElementById('addvidbutton')).value;
    this.screen_to_show = 22;
  }
   /* addbook(): void {
        const addtype = (<HTMLInputElement>document.getElementById('addbookbutton')).value;
        let e: Json;
        let fd = new FormData();
        let obj = {file: fd};
        let file: any;
        fd.append('selectFile', file, file.name);
        let url = this.base_url + 'image/new';
        let thumnail_key: any;
        let searchParams = new URLSearchParams;
        let options = new RequestOptions({params: searchParams});
        /*e.title = this.title;
        e.author = this.author;
        e.long_desc = this.long_desc;
        e.short_desc = this.short_desc;*/
    /*    try {
             this.http.post(url, Json , options).subscribe(res => {
            console.log(res);
            console.log(res.json());
            thumnail_key = res.json().thumnail_key;
         }, error => console.error(error));
        } catch (any) {
          console.log("Search failed");
        }


        url = this.base_url + "content/new";
        let content_key: any;
        let size: any;
        let request: Json;
        request.content_key = content_key;
        request.thumbnail_key = thumnail_key;
        request.size = size;
        try {
             this.http.post(url, Json , options).subscribe(res => {
            console.log(res);
            console.log(res.json());
            content_key = res.json().content_key;
            size = res.json().size;
         }, error => console.error(error));
        } catch (any) {
          // Handle errors here.
          console.log("Search failed");
        }
        url = this.base_url + "metadata/new";
        try {
            this.http.post(url, request , options).subscribe(res => {
           console.log(res);
           console.log(res.json());
        }, error => console.error(error));
       } catch (any) {
         // Handle errors here.
         console.log("Search failed");
       }

       // if (addtype === 'Submit') {
            this.screen_to_show = 20;
            this.screen_to_show = 21;
       // }
    }
*/
    public uploadImage(FormData: any) {
        let url = this.base_url + 'image/new';
       try {
           return  this.http.post(url, FormData);
       } catch (any) {
            console.log("upload Failed");
        }
    }
   add(): void {
    const addtype = (<HTMLInputElement>document.getElementById('Material-Dropdown')).value;
        if (addtype === 'Document') {
            this.screen_to_show = 1;
        } else if (addtype === 'Video') {
            this.screen_to_show = 2;
        } else if (addtype === 'Testassessment') {
            this.screen_to_show = 4; }
  }
  modifyDoc(): void {
    let url = this.base_url + "search";
    let searchParams = new URLSearchParams();
    searchParams.append('genre', this.subject);
    let options = new RequestOptions({ params: searchParams });
    try {
    this.http.get(url, options).subscribe(res => {
        console.log(res);
        console.log(res.json());
        this.results = res.json();
    }, error => console.error(error));
    } catch (any) {
    console.log("Modify failed");
    }
}
modifyDoc1(): void {
    const addtype = (<HTMLInputElement>document.getElementById('modifybookbutton')).value;
    this.screen_to_show = 29;

}
modifyvid(): void {
    const addtype = (<HTMLInputElement>document.getElementById('modifyvidbutton')).value;
    this.screen_to_show = 27;
}
deleteDoc(): void {
        let url = this.base_url + "metadata/" + this.$oid;
        let searchParams = new URLSearchParams();
        let options = new RequestOptions({ params: searchParams });
        try {
        this.http.delete(url, options).subscribe(res => {
            console.log(res);
        }, error => console.error(error));
        } catch (any) {
        console.log("Delete failed");
        }
    }
}

