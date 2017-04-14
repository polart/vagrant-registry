import React, {Component} from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";
import Moment from "moment";
import BoxOrdering from "./BoxOrdering";
import MyPagination from "./MyPagination";


export default class BoxList extends Component {
  onBoxClick = (e) => {
    e.preventDefault();
    this.props.router.push(
        // Relative url
        e.currentTarget.getAttribute("href")
    );
    return false;
  };

  renderBoxesList = () => {
    if (!this.boxPages) {
      return <p>Loading...</p>
    }
    if (this.boxPages.count === 0) {
      return <p>No boxes</p>
    }

    const boxTags = this.boxPages.pages[this.activePage] || [];

    return boxTags.map(tag => {
      const box = this.props.boxes[tag];
      return (
          <ListGroupItem
              key={box.tag}
              href={`/boxes/${box.tag}`}
              onClick={this.onBoxClick}
          >
            <div>
              <h4>{box.tag}</h4>
              <p>{box.short_description}</p>
            </div>
            <div>{box.pulls} pulls</div>
            <small title={Moment(box.date_updated).format('LLL')}>
              Last updated: {Moment(box.date_updated).fromNow()}
            </small>
            {/*<div className="clearfix"></div>*/}
          </ListGroupItem>
      );
    });
  };

  render() {
    this.activePage = parseInt(this.props.router.location.query.page || 1, 10);
    this.boxPages = this.props.boxesPages;
    const boxCount = (this.boxPages && this.boxPages.count) || 0;
    return (
        <div>
          <BoxOrdering router={this.props.router} />
          <ListGroup>
            {this.renderBoxesList()}
          </ListGroup>
          <MyPagination
              router={this.props.router}
              itemsCount={boxCount}
          />
        </div>
    );
  }
}
