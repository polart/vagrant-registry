import React, {Component} from "react";
import {ListGroupItem} from "react-bootstrap";
import Moment from "moment";
import Filesize from "filesize";


export default class BoxProviderList extends Component {
  renderProvidersList = () => {
    if (!this.props.providers) {
      return;
    }

    return this.props.providers.map(provider => {
      return (
          <ListGroupItem
              key={provider.tag}
          >
            <h4 className="list-group-item-heading">
              {provider.provider} |&nbsp;
              <small title={Moment(provider.date_updated).format('LLL')}>
                Last updated: {Moment(provider.date_updated).fromNow()}
              </small>
            </h4>
            <p>Size: {Filesize(provider.file_size)}</p>
            <a href={provider.download_url} className="btn btn-default">
              Download box
            </a>
          </ListGroupItem>
      );
    });
  };

  render() {
    return (
      <div>
        <h4>Providers</h4>
        {this.renderProvidersList()}
      </div>
    );
  }
}
