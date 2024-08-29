def generateHTML(movies, filePath, sort_type='rating', min_votes_kp=10, min_votes_imdb=50, useMagnet=False):
    f = open(filePath, 'w', encoding='utf-8')
    html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="ru-RU">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow, noarchive, noodp, noydir, nosnippet" />
<meta content="width=960" name="viewport">
<title>Новые цифровые релизы</title>
<style type="text/css">
  html {
      background-color: #e6e6e6;
      min-width: 1024px;
      width: 100%;
      position: relative;
  }

  body {
      background: #e6e6e6;
      color: #333;
      font-family: tahoma,verdana,arial;
      margin: 0;
      padding: 0 0 22px 0;
  }

  * {
      outline: 0;
  }

  .shadow {
      box-shadow: 0px 10px 20px 0px rgba(0, 0, 0, 0.2);
      width: 850px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
  }

  .block1 {
      width: 850px;
      position: relative;
      margin: 0 auto;
  }
  .sbb {
      background-color: #f2f2f2;
      text-align: right;
      padding-right:10px;
  }
  .sButton {
    display: inline-block;
    background:none;
    border:none;
    margin-left: 10px;
    margin-right: 10px;
    padding:0;
    padding-top:10px;
    cursor: pointer;
    text-decoration: underline;
    font-family: tahoma,verdana,arial;
    font-size: 13px;
  }
"""
    if (sort_type == "torrentsDate"):
        html += """  #sortButton1 {
  }
  #sortButton2 {
  color: #f60;
  }"""
    else:
        html += """  #sortButton1 {
  color: #f60;
  }
  #sortButton2 {
  }"""
    html += """
  .block2 {
      position: relative;
      background-color: #f2f2f2;
      width: 100%;
  }

  .block2::before, .block2::after {
      content: "";
      display: table;
  }

  .block2::after, .photoInfoTable::after {
      clear: both;
  }

  .photoInfoTable::before, .photoInfoTable::after {
      content: "";
      display: table;
  }

  .photoInfoTable {
      width: 850px;
      float: left;
  }

  .headerFilm h1 {
      margin: 0;
      padding: 0;
  }

  .headerFilm {
      width: 820px;
      padding: 20px 15px 20px 15px;
      position: relative;
  }


  H1.moviename {
      vertical-align: middle;
      padding-left: 0px;
      margin: 5px 0;
      font-size: 25px;
      font-weight: normal;
  }

  H1 {
      font-size: 25px;
      font-weight: normal;
      color: #000;
  }

  .headerFilm > span {
      color: #666;
      font-size: 13px;
  }

  .film-img-box {
      margin-left: 0;
      position: relative;
      left: -12px;
      min-height: 205px;
      margin-bottom: 15px;
  }

  .film-img-box img {
      border: 0;
  }

  .photoBlock {
      width: 223px;
      padding: 0 0 0 0;
      float: left;
      position: relative;
      font-size: 11px;
  }

  .movie-buttons-container {
      margin-bottom: 20px;
  }

  .torrentbutton {
      cursor: pointer;
      border: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      background-color: #f60;
      border-radius: 3px;
      color: #fff;
      font: 12px Arial, sans-serif;
      line-height: 180%;
      font-weight: bold;
      height: 70px;
      -webkit-transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      -moz-transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      text-align: center;
      text-decoration: none;
      width: 170px;
      margin: 10px 0 10px 15px;
      display:inline-block;
  }
  .torrentbuttonstar {
      cursor: pointer;
      border: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      border-radius: 3px;
      color: #fff;
      font: 12px Arial, sans-serif;
      line-height: 180%;
      font-weight: bold;
      height: 70px;
      -webkit-transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      -moz-transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      text-align: center;
      text-decoration: none;
      width: 170px;
      margin: 10px 0 10px 15px;
      display:inline-block;
      background: #f60 no-repeat url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHZpZXdCb3g9JzAgMCAzMS4y MDEgMjkuNjc2Jz48cG9seWdvbiBwb2ludHM9JzE1LjYwMiwwIDE5LjMyNSwxMS4yNzkgMzEuMiwx MS4zMzIgMjEuNjI0LDE4LjM2IDI1LjI0MywyOS42NzYgMTUuNjAyLDIyLjczOCA1Ljk2LDI5LjY3 NiA5LjU3NywxOC4zNiAwLDExLjMzMiAxMS44NzgsMTEuMjc5JyBmaWxsPScjRkZGRkZGJyAvPjwv c3ZnPg==");
      background-size: 10px 10px;
      background-position: 3px 3px;
  }

  .trailersbutton {
      cursor: pointer;
      border: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      background-color: rgba(68, 68, 68, 0.9);
      border-radius: 3px;
      color: #fff;
      font: 12px Arial, sans-serif;
      line-height: normal;
      font-weight: bold;
      height: 35px;
      -webkit-transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      -moz-transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      transition: background-color 0.1s, color 0.1s, border-color 0.1s;
      text-align: center;
      text-decoration: none;
      width: 170px;
      margin: 10px 0 10px 15px;
      display:inline-block;
  }

  .infoTable {
      float: left;
      display: block;
  }

  .infoTable .info {
      width: 610px;
  }

  .info, .info * {
      border-collapse: collapse;
      margin: 0;
      padding: 0;
  }

  .info tr {
      border-bottom: #DFDFDF solid 1px; 
      font-family: tahoma,verdana,arial;
      font-size: 13px;
  }

  .info .type {
      color: #f60;
      width: 140px;
      padding-left: 27px;
  }

  .info td {
      min-height: 14px;
      vertical-align: top;
      padding-bottom: 9px;
      padding: 6px 0 6px 20px;
  }

  td {
      font-family: tahoma,verdana,arial;
      font-size: 13px;
      color: #000;
  }

  .film-rating {
      border-radius: 1px;
      position: absolute;
      left: 5px;
      top: 5px;
      z-index: 5;
      box-shadow: none;
      color: #fff;
      width: 32px;
      font-size: 11px;
      font-weight: 600;
      line-height: 13px;
      padding: 3px 0 2px;
      text-align: center;
      font-family: Arial,Tahoma,Verdana,sans-serif;
  }
  div.tddata {
      font-family: tahoma,verdana,arial;
      font-size: 13px;
      text-overflow: ellipsis;
      white-space: normal; #nowrap;
      overflow: hidden;
      width:423px;
  }
  div.description {
      font-family: tahoma,verdana,arial;
      font-size: 13px;
      color: #000;
      padding-top: 20px;
      padding-bottom: 20px;
      width:610px;
  }
</style>
<script>
function sortElements(sortType){
    var container = document.getElementsByClassName('block1')[0];
    var newContainer = container.cloneNode(false);

    var items = [];
    for(var i = container.childNodes.length; i--;){
        if(container.childNodes[i].nodeName === 'DIV')
            items.push(container.childNodes[i]);
    }
    
    if(sortType === "torrentDate") {
    items.sort(function(a, b){
       var aDate = new Date(a.getAttribute('data-torrentDate'));
       var bDate = new Date(b.getAttribute('data-torrentDate'));
       return (Number(bDate) - Number(aDate));
    });
    } else {
    items.sort(function(a, b){
       return (Math.round(parseFloat(b.getAttribute('data-rating'))*10) - Math.round(parseFloat(a.getAttribute('data-rating'))*10));
    });
    }
    
    for(var i = 0; i < items.length; i++)
        newContainer.appendChild(items[i]);
    container.parentNode.replaceChild(newContainer, container);
}

function sortRating(){
    element = document.getElementById("sortButton1");
    style = getComputedStyle(element);
    if (style.color != "rgb(0, 0, 0)") {
        return 0;
    }
    sortElements("rating");
    document.getElementById("sortButton2").style.color = "black";
    document.getElementById("sortButton1").style.color = "#f60";
}

function sortTorrentsDate(){
    element = document.getElementById("sortButton2");
    style = getComputedStyle(element);
    if (style.color != "rgb(0, 0, 0)") {
        return 0;
    }
    sortElements("torrentDate");
    document.getElementById("sortButton1").style.color = "black";
    document.getElementById("sortButton2").style.color = "#f60";
}
</script>
</head>
<body>
  <div class="shadow">
    <div class="sbb">
      <button id="sortButton1" class="sButton" onclick="sortRating()">по рейтингу</button>
      <button id="sortButton2" class="sButton" onclick="sortTorrentsDate()">по дате торрент-релиза</button>
    </div>
    <div class="block1" style="background-color: #f2f2f2;">"""
    descriptionTemplate = """
                <tr>
                  <td class="type">{}</td>
                  <td>
                    <div class="tddata" style="position: relative">
                        {}
                    </div>
                  </td>
                </tr>"""
    buttonsTemplate = """<button class="torrentbutton" style="" onclick="location.href='{}'">{}</button>"""
    buttonsTemplateS = """          <button class="torrentbuttonstar" style="" onclick="location.href='{}'">{}</button>"""
    movieTemplate = """      <div class="block2" data-releaseDate="{}" data-torrentDate="{}" data-rating="{}" data-comboDate="{}">
        <div class="photoInfoTable">
          <div class="headerFilm">
            <h1 class="moviename" itemprop="name">{}</h1>
            <span itemprop="alternativeHeadline" style="{}">{}</span>
          </div>
          <div class="photoBlock">
            <div class="film-img-box">
              <div class="film-rating" style="{}">{}</div> 
              <img src="{}" alt="{}" itemprop="image" width="218"></img>
            </div>
            <div class="movie-buttons-container">
              <button class="trailersbutton" style="" onclick="window.open('{}','_blank');">Трейлеры</button>
            </div>
          </div>
          <div class="infoTable">
            <table class="info">
              <tbody>
{}
              </tbody>
            </table>
            <div class="description" style="position: relative;">{}</div>
          </div>
        </div>
        <div class="movie-buttons-container">
{}
        </div>
      </div>
"""
    for movie in movies:

        descriptionBlock = ""
        descriptionBlock += descriptionTemplate.format("год", movie["year"])
        descriptionBlock += descriptionTemplate.format(
            "страна", movie["country"])
        descriptionBlock += descriptionTemplate.format(
            "режиссёр", movie["directors"])
        descriptionBlock += descriptionTemplate.format(
            "актёры", movie["actors"])
        descriptionBlock += descriptionTemplate.format("жанр", movie["genre"])
        if len(movie["ratingAgeLimits"]) > 0:
            try:
                if movie["ratingAgeLimits"] == 'age0':
                    descriptionBlock += descriptionTemplate.format(
                        "возраст", "любой")
                elif movie["ratingAgeLimits"] == 'age6':
                    descriptionBlock += descriptionTemplate.format(
                        "возраст", "от 6 лет")
                elif movie["ratingAgeLimits"] == 'age12':
                    descriptionBlock += descriptionTemplate.format(
                        "возраст", "от 12 лет")
                elif movie["ratingAgeLimits"] == 'age16':
                    descriptionBlock += descriptionTemplate.format(
                        "возраст", "от 16 лет")
                else:
                    descriptionBlock += descriptionTemplate.format(
                        "возраст", "от 18 лет")
            except:
                pass
        elif len(movie["ratingMPAA"]) > 0:
            if movie["ratingMPAA"] == "g":
                descriptionBlock += descriptionTemplate.format(
                    "возраст", "любой")
            elif movie["ratingMPAA"] == "pg":
                descriptionBlock += descriptionTemplate.format(
                    "возраст", "от 6 лет")
            elif movie["ratingMPAA"] == "pg13":
                descriptionBlock += descriptionTemplate.format(
                    "возраст", "от 12 лет")
            elif movie["ratingMPAA"] == "r":
                descriptionBlock += descriptionTemplate.format(
                    "возраст", "от 16 лет")
            else:
                descriptionBlock += descriptionTemplate.format(
                    "возраст", "от 18 лет")
        try:
            filmLength = str(movie["filmLength"] // 60) + \
                ":" + str(movie["filmLength"] % 60) + " ч"
        except:
            filmLength = "-"
        descriptionBlock += descriptionTemplate.format(
            "продолжительность", filmLength)

        if len(str(movie["ratingKP"])) > 0:
            rKP = movie["ratingKP"]
        else:
            if movie["ratingKPCount"] == 0:
                rKP = "нет"
            elif movie["ratingKPCount"] < min_votes_kp:
                rKP = "мало голосов"
            else:
                rKP = "нет"

        descriptionBlock += descriptionTemplate.format(
            "рейтинг КиноПоиск", "<a href=\"{}\" style=\"text-decoration: underline; color:black\" target=\"_blank\">{}</a>".format(movie["webURL"], rKP))

        if len(str(movie["ratingIMDb"])) > 0:
            rIMDb = movie["ratingIMDb"]
        else:
            if movie["ratingIMDbCount"] == 0:
                rIMDb = "нет"
            elif movie["ratingIMDbCount"] < min_votes_imdb:
                rIMDb = "мало голосов"
            else:
                rIMDb = "нет"

        descriptionBlock += descriptionTemplate.format("рейтинг IMDb", rIMDb)

        # prHeader = "премьера"
        # if movie["premierType"] == "digital":
        # 	prHeader = "цифровая премьера"
        # elif movie["premierType"] == "ru":
        # 	prHeader = "премьера в России"
        # descriptionBlock += descriptionTemplate.format(prHeader, movie["premierDate"].strftime("%d.%m.%Y"))
        # descriptionBlock += descriptionTemplate.format("торрент-релиз", "<a href=\"{}\" style=\"text-decoration: underline; color:black\" target=\"_blank\">{}</a> ({})".format("http://rutor.info/search/0/0/010/0/film%20" + movie["filmID"], movie["torrentsDate"].strftime("%d.%m.%Y"), movie["torrentsDateType"]))
        descriptionBlock += descriptionTemplate.format(
            "торрент-релиз", "{}".format(movie["torrentsDate"].strftime("%d.%m.%Y")))
        # descriptionBlock += descriptionTemplate.format("описание", movie["description"])
        descriptionBlock += descriptionTemplate.format(
            "тип торрент-релиза", movie["torrentsDateType"])

        torrents = movie["torrents"]
        buttonsBlock = ""
        for torrent in torrents:
            size = f'''{torrent["size"]//(1024*1024*1024)}.{str(torrent["size"]%(1024*1024*1024))[0:2]}'''
            if "rutor" in torrent["link"]:
                site = 'Rutor.info'
            else:
                site = 'MegaPeer.vip'
            if torrent["license"]:
                if useMagnet:
                    buttonsBlock += buttonsTemplateS.format(
                        torrent["magnet"], f'''{site} {size} Гб<br>{torrent["type"]}<br>S:{torrent['seeders']} L:{torrent['leechers']}''')
                else:
                    buttonsBlock += buttonsTemplateS.format(
                        torrent["link"], f'''{site} {size} Гб<br>{torrent["type"]}<br>S:{torrent['seeders']} L:{torrent['leechers']}''')
            else:
                if useMagnet:
                    buttonsBlock += buttonsTemplate.format(
                        torrent["magnet"], f'''{site} - {size} Гб<br>{torrent["type"]}<br>S:{torrent['seeders']} L:{torrent['leechers']}''')
                else:
                    buttonsBlock += buttonsTemplate.format(
                        torrent["link"], f'''{site} {size} Гб<br>{torrent["type"]}<br>S:{torrent['seeders']} L:{torrent['leechers']}''')
        buttonsBlock += buttonsTemplate.format(
            torrent["page"], "<br>Cтраница торрента<br><br>")
        displayOrigName = "display: none;"
        if len(movie["nameOriginal"]) > 0:
            displayOrigName = ""

        ratingStyle = "background-color: #aaa;"
        if movie["ratingFloat"] >= 7:
            ratingStyle = "background-color: #3bb33b;"
        elif movie["ratingFloat"] < 5.5:
            ratingStyle = "background-color: #b43c3c;"

        rating = movie["rating"]
        if movie["ratingFloat"] < 1:
            ratingStyle = "display: none;"
            rating = "—"

        html += movieTemplate.format(movie["torrentsDate"].strftime("%Y-%m-%d"), movie["torrentsDate"].strftime("%Y-%m-%d"), movie["rating"], movie["torrentsDate"].strftime("%Y-%m-%d"), movie["nameRU"], displayOrigName,
                                     movie["nameOriginal"], ratingStyle, rating, movie["posterURL"], movie["nameRU"], "https://www.kinopoisk.ru/film/{}/video/".format(movie["filmID"]), descriptionBlock, movie["description"], buttonsBlock)

        # html += movieTemplate.format(movie["torrentsDate"].strftime("%Y-%m-%d"), movie["torrentsDate"].strftime("%Y-%m-%d"), movie["rating"], movie["torrentsDate"].strftime("%Y-%m-%d"), movie["nameRU"], displayOrigName, movie["nameOriginal"], ratingStyle, rating, movie["posterURL"], movie["nameRU"], movie["trailerURL"], descriptionBlock, movie["description"], buttonsBlock)
    html += """    </div>
  </div>
</body>
</html>"""
    f.write(html)
    f.close()
    return
